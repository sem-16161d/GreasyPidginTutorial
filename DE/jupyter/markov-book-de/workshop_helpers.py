"""
workshop_helpers.py

Small helpers for the GreasyPidgin "Markov chains & MIDI" workshop book.

They keep the notebooks short by hiding everything that is not about music:
uploading a file, listening to the result, drawing a piano roll. All the
musical work (reading MIDI, learning Markov chains, building and exporting
gestures) is done with GreasyPidgin itself, in the notebooks.

Nothing in here needs anything but numpy, matplotlib, mido and GreasyPidgin.
"""

from __future__ import annotations

import base64
import contextlib
import io
import os
import sys
from dataclasses import dataclass, field

import numpy as np

IN_COLAB = "google.colab" in sys.modules

# GreasyPidgin's own spelling (scientific pitch notation): lower case, s = sharp, f = flat
NOTE_NAMES = ["c", "cs", "d", "ef", "e", "f", "fs", "g", "af", "a", "bf", "b"]

# ---------------------------------------------------------------------------
# Language ("en" or "de"): set with set_language("de") at the top of a notebook
# ---------------------------------------------------------------------------

LANG = "en"

_TEXT = {
    "en": {
        "not_found": "'{path}' not found -> using the demo melody instead.",
        "choose": "Choose a MIDI file (.mid) from your computer.\n"
                  "No file? Just cancel the dialog and the demo melody is used.",
        "using": "Using {name}",
        "no_upload": "No MIDI file uploaded -> using the demo melody.",
        "no_colab": "Not running in Colab: no upload dialog. "
                    "Use choose_midi('your_file.mid') to load your own file. Using the demo melody.",
        "no_notes": "No notes found in {path}",
        "too_short": "Only {n} notes found on track {track} - too short.",
        "beats": "beats",
        "your_melody": "Your melody",
        "next": "next",
        "current": "current",
        "probability": "probability",
        "states_cut": "{n} states - showing the first {m}.",
        "nothing_to_play": "No notes to play.",
        "saved_as": "Saved as {path}",
        "packed": "Packed:",
    },
    "de": {
        "not_found": "'{path}' nicht gefunden -> stattdessen wird die Demo-Melodie verwendet.",
        "choose": "Wähle eine MIDI-Datei (.mid) von deinem Computer.\n"
                  "Keine Datei zur Hand? Brich den Dialog einfach ab, dann wird die Demo-Melodie verwendet.",
        "using": "Verwende {name}",
        "no_upload": "Keine MIDI-Datei hochgeladen -> die Demo-Melodie wird verwendet.",
        "no_colab": "Nicht in Colab: es gibt keinen Upload-Dialog. "
                    "Mit choose_midi('deine_datei.mid') lädst du eine eigene Datei. Es wird die Demo-Melodie verwendet.",
        "no_notes": "Keine Noten gefunden in {path}",
        "too_short": "Nur {n} Noten auf Spur {track} gefunden - zu kurz.",
        "beats": "Schläge",
        "your_melody": "Deine Melodie",
        "next": "als Nächstes",
        "current": "aktuell",
        "probability": "Wahrscheinlichkeit",
        "states_cut": "{n} Zustände - gezeigt werden die ersten {m}.",
        "nothing_to_play": "Keine Noten zum Abspielen.",
        "saved_as": "Gespeichert als {path}",
        "packed": "Eingepackt:",
    },
}


def set_language(lang: str) -> None:
    """Choose the language of messages and labels: "en" or "de"."""
    global LANG
    if lang not in _TEXT:
        raise ValueError(f"Unknown language {lang!r}; use 'en' or 'de'.")
    LANG = lang


def _t(key: str, **kw) -> str:
    return _TEXT[LANG][key].format(**kw)


def pitch_class_name(pc) -> str:
    """0 -> 'c', 3 -> 'ef'. Same spelling in every language (German H is 'b', German B is 'bf')."""
    return NOTE_NAMES[int(round(float(pc))) % 12]


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

def pitch_name(midi) -> str:
    """60 -> 'c4', 61 -> 'cs4', 58 -> 'bf3' (the names GreasyPidgin's spntom reads). Non-numbers are returned as text."""
    try:
        m = int(round(float(midi)))
    except (TypeError, ValueError):
        return str(midi)
    return f"{pitch_class_name(m)}{m // 12 - 1}"


def _quiet():
    """Silence prints from library calls (GreasyPidgin is chatty)."""
    return contextlib.redirect_stdout(io.StringIO())


def quantise_to(value: float, step: float) -> float:
    """Round to the nearest multiple of `step` (never below one step)."""
    return max(step, round(value / step) * step)


# ---------------------------------------------------------------------------
# Demo melody and upload
# ---------------------------------------------------------------------------

# Three public-domain tunes in C major, one after another: (MIDI pitch, beats)
_C, _D, _E, _F, _G, _A = 60, 62, 64, 65, 67, 69

def _tune(*notes):
    """notes: pitch or (pitch, beats); a plain pitch lasts one beat."""
    return [(n, 1.0) if isinstance(n, int) else n for n in notes]

_DEMO = (
    # Ode to Joy (Beethoven)
    _tune(_E, _E, _F, _G, _G, _F, _E, _D, _C, _C, _D, _E, (_E, 1.5), (_D, .5), (_D, 2),
          _E, _E, _F, _G, _G, _F, _E, _D, _C, _C, _D, _E, (_D, 1.5), (_C, .5), (_C, 2))
    # Frere Jacques
    + _tune(_C, _D, _E, _C, _C, _D, _E, _C, _E, _F, (_G, 2), _E, _F, (_G, 2),
            (_G, .5), (_A, .5), _G, _F, _E, _C, (_G, .5), (_A, .5), _G, _F, _E, _C,
            _C, (_G - 12, 1), (_C, 2), _C, (_G - 12, 1), (_C, 2))
    # Twinkle, twinkle, little star
    + _tune(_C, _C, _G, _G, _A, _A, (_G, 2), _F, _F, _E, _E, _D, _D, (_C, 2),
            _G, _G, _F, _F, _E, _E, (_D, 2), _G, _G, _F, _F, _E, _E, (_D, 2),
            _C, _C, _G, _G, _A, _A, (_G, 2), _F, _F, _E, _E, _D, _D, (_C, 2))
)


def make_demo_midi(path: str = "demo_melody.mid", bpm: float = 100.0) -> str:
    """Write the built-in demo melody (three well-known tunes in a row) as a MIDI file."""
    import mido

    tpb = 480
    mid = mido.MidiFile(ticks_per_beat=tpb)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    for pitch, beats in _DEMO:
        ticks = int(round(beats * tpb))
        track.append(mido.Message("note_on", note=pitch, velocity=80, time=0))
        track.append(mido.Message("note_off", note=pitch, velocity=0, time=ticks))
    mid.save(path)
    return path


def choose_midi(path: str | None = None, use_demo: bool = False) -> str:
    """
    Return the path of the MIDI file to work with.

    In Google Colab a file dialog opens: pick a .mid file from your computer.
    Cancel the dialog (or pass use_demo=True) to use the built-in demo.

    Outside Colab, pass the file name: choose_midi("my_song.mid").
    Without one, the demo melody is used.
    """
    if use_demo:
        return make_demo_midi()

    if path:
        if os.path.exists(path):
            return path
        print(_t("not_found", path=path))
        return make_demo_midi()

    if IN_COLAB:
        from google.colab import files

        print(_t("choose"))
        uploaded = files.upload()
        names = [n for n in uploaded if n.lower().endswith((".mid", ".midi"))]
        if names:
            print(_t("using", name=names[0]))
            return names[0]
        print(_t("no_upload"))
        return make_demo_midi()

    print(_t("no_colab"))
    return make_demo_midi()


# ---------------------------------------------------------------------------
# Melody: a MIDI file reduced to what a Markov chain needs
# ---------------------------------------------------------------------------

@dataclass
class Melody:
    """A monophonic melody extracted from a MIDI file."""
    pitches:   list                     # MIDI note numbers (int)
    onsets:    list                     # start of each note, in beats
    durations: list                     # length of each note, in beats
    deltas:    list                     # inter-onset intervals in beats, quantised
    bpm:       float
    path:      str = ""
    track:     int = 0
    gesture:   object = field(default=None, repr=False)

    def __len__(self) -> int:
        return len(self.pitches)

    def __repr__(self) -> str:
        names = " ".join(pitch_name(p) for p in self.pitches[:12])
        more = " ..." if len(self.pitches) > 12 else ""
        return (f"Melody({len(self)} notes, {self.bpm:.0f} bpm, track {self.track}: "
                f"{names}{more})")


def _busiest_track(path: str) -> int:
    import mido

    mid = mido.MidiFile(path)
    counts = []
    for i, tr in enumerate(mid.tracks):
        n = sum(1 for m in tr if m.type == "note_on" and m.velocity > 0)
        counts.append((n, -i))
    if not counts or max(counts)[0] == 0:
        raise ValueError(_t("no_notes", path=path))
    return -max(counts)[1]


def load_melody(path: str, track: int | None = None, quantise: float = 0.25) -> Melody:
    """
    Read a MIDI file with GreasyPidgin and reduce it to one melody line.

    - track:    which MIDI track to read (default: the one with the most notes)
    - quantise: inter-onset times are rounded to multiples of this many beats
                (0.25 = sixteenth notes), so rhythms become a small set of
                symbols a Markov chain can learn.
    - chords:   if several notes start together, the highest one is kept.
    """
    from GreasyPidgin import Gesture

    if track is None:
        track = _busiest_track(path)

    with _quiet():
        g = Gesture.fromMidiFile(path, trackNumber=track)

    notes = []
    for ph in g.children:
        if not ph.allPitches:
            continue
        notes.append((float(ph.startTimeBeats), float(ph.durationBeats),
                      int(round(max(ph.allPitches)))))
    notes.sort()

    # keep only the highest note of each chord
    reduced = []
    for start, dur, pitch in notes:
        if reduced and abs(reduced[-1][0] - start) < 1e-3:
            if pitch > reduced[-1][2]:
                reduced[-1] = (start, dur, pitch)
        else:
            reduced.append((start, dur, pitch))

    if len(reduced) < 4:
        raise ValueError(_t("too_short", n=len(reduced), track=track))

    onsets = [n[0] for n in reduced]
    durations = [n[1] for n in reduced]
    pitches = [n[2] for n in reduced]
    iois = [onsets[i + 1] - onsets[i] for i in range(len(onsets) - 1)] + [durations[-1]]
    deltas = [quantise_to(x, quantise) for x in iois]

    return Melody(pitches, onsets, durations, deltas,
                  float(g.data.get("bpm", 120.0)), path, track, g)


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_notes(pitches, deltas=None, durations=None, *, title="", ax=None, color="C0"):
    """Piano roll of a note list. deltas = inter-onset times in beats (default 1)."""
    import matplotlib.pyplot as plt

    n = len(pitches)
    deltas = [1.0] * n if deltas is None else [deltas[i % len(deltas)] for i in range(n)]
    starts = np.concatenate([[0.0], np.cumsum(deltas)[:-1]])
    if durations is None:
        durations = deltas
    else:
        durations = [durations[i % len(durations)] for i in range(n)]

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 2.8))
    for s, d, p in zip(starts, durations, pitches):
        ax.barh(p, d * 0.95, left=s, height=0.8, color=color)
    lo, hi = int(min(pitches)), int(max(pitches))
    ticks = [m for m in range(lo, hi + 1) if m % 12 == 0 or m in (lo, hi)]
    ax.set_yticks(ticks)
    ax.set_yticklabels([pitch_name(t) for t in ticks])
    ax.set_xlabel(_t("beats"))
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.3)
    return ax


def plot_melody(melody: Melody, **kw):
    """Piano roll of a Melody."""
    return plot_notes(melody.pitches, melody.deltas, melody.durations,
                      title=kw.pop("title", _t("your_melody")), **kw)


def plot_transition_matrix(chain, *, label=pitch_name, ax=None, max_states=40):
    """
    Heat map of a MarkovChain's rules: row = current state, column = next symbol,
    brightness = probability. Higher-order states are written as 'C4 D4'.
    """
    import matplotlib.pyplot as plt

    rules = chain.rules
    states = sorted(rules.elements)
    symbols = sorted(rules.flatElements)
    if len(states) > max_states:
        print(_t("states_cut", n=len(states), m=max_states))
        states = states[:max_states]

    m = np.zeros((len(states), len(symbols)))
    for i, st in enumerate(states):
        r = rules[st]
        for nxt, w in zip(r.nextElements, r.weights):
            m[i, symbols.index(nxt)] = w

    if ax is None:
        _, ax = plt.subplots(figsize=(max(5, 0.4 * len(symbols) + 2),
                                      max(3, 0.28 * len(states) + 1.5)))
    im = ax.imshow(m, cmap="viridis", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(symbols)))
    ax.set_xticklabels([label(s) for s in symbols], rotation=90)
    ax.set_yticks(range(len(states)))
    ax.set_yticklabels([" ".join(label(s) for s in st) for st in states])
    ax.set_xlabel(_t("next"))
    ax.set_ylabel(_t("current"))
    ax.figure.colorbar(im, ax=ax, label=_t("probability"))
    return ax


def copy_ratio(original, generated, n: int = 4) -> float:
    """
    How much of the new melody is copied? The share of n-note groups in
    `generated` that also occur, unchanged, in `original` (0 = all new, 1 = all copied).
    """
    original, generated = list(original), list(generated)
    if len(generated) < n or len(original) < n:
        return float("nan")
    orig = {tuple(original[i:i + n]) for i in range(len(original) - n + 1)}
    gen = [tuple(generated[i:i + n]) for i in range(len(generated) - n + 1)]
    return sum(g in orig for g in gen) / len(gen)


# ---------------------------------------------------------------------------
# From note lists to a MIDI file
# ---------------------------------------------------------------------------

def render_midi(pitches, deltas, bpm: float, path: str = "new_melody.mid", *,
                dynamics=80, legato: float = 0.9):
    """
    Turn a list of pitches and inter-onset times (in beats) into a GreasyPidgin
    Gesture and write it as a MIDI file. `deltas` is cycled if it is shorter
    than `pitches`. Returns the Gesture.

    Same recipe as in chapter 2 -- just packed into one call.
    """
    from GreasyPidgin import Gesture

    n = len(pitches)
    deltas = [float(deltas[i % len(deltas)]) for i in range(n)]
    gesture = Gesture.fromLists(
        size=n,
        startOffset=0,
        startDeltas=[0.0] + deltas[:-1],
        durations=[d * legato for d in deltas],
        pitches=list(pitches),
        dynamics=dynamics,
        timeUnit="b",
        bpm=bpm,
    )
    with _quiet():
        gesture.toMidi(path, bpm=bpm)
    return gesture


# ---------------------------------------------------------------------------
# Listening and downloading
# ---------------------------------------------------------------------------

def _midi_notes(path: str):
    """(start_sec, dur_sec, pitch, velocity) for every note in a MIDI file."""
    import mido

    mid = mido.MidiFile(path)
    notes, open_ = [], {}
    t = 0.0
    for msg in mid:                       # iterating a MidiFile yields delta times in seconds
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            open_.setdefault((msg.channel, msg.note), []).append((t, msg.velocity))
        elif msg.type in ("note_off", "note_on"):
            stack = open_.get((msg.channel, msg.note))
            if stack:
                t0, vel = stack.pop(0)
                notes.append((t0, max(t - t0, 0.05), msg.note, vel))
    return sorted(notes)


def synth_midi(path: str, sr: int = 16000, max_seconds: float | None = None) -> np.ndarray:
    """A very simple additive synth, so every MIDI file can be heard anywhere."""
    notes = _midi_notes(path)
    if max_seconds is not None:
        notes = [n for n in notes if n[0] < max_seconds]
    if not notes:
        raise ValueError(_t("nothing_to_play"))
    total = max(s + d for s, d, _, _ in notes) + 0.8
    out = np.zeros(int(total * sr) + 1)
    for start, dur, pitch, vel in notes:
        f = 440.0 * 2 ** ((pitch - 69) / 12)
        length = dur + 0.4
        t = np.arange(int(length * sr)) / sr
        tone = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
                + 0.15 * np.sin(2 * np.pi * 3 * f * t))
        env = np.exp(-2.2 * t) * np.minimum(1.0, t / 0.01)
        env *= np.where(t > dur, np.exp(-12 * (t - dur)), 1.0)
        i0 = int(start * sr)
        out[i0:i0 + len(t)] += tone * env * (vel / 127) * 0.25
    peak = np.max(np.abs(out))
    return out / peak * 0.9 if peak > 0 else out


def listen(path: str, engine: str = "auto", max_seconds: float | None = 20.0):
    """
    Play a MIDI file in the notebook.

    engine = "web"   nicer piano sound (needs internet; default in Colab)
             "synth" simple built-in synthesiser (works everywhere); plays only the
                     first `max_seconds` (default 20) to keep notebooks small
             "auto"  web in Colab, synth elsewhere
    """
    from IPython.display import HTML, Audio, display

    if engine == "auto":
        engine = "web" if IN_COLAB else "synth"

    if engine == "web":
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        display(HTML(f"""
<script src="https://cdn.jsdelivr.net/combine/npm/tone@14.7.58,npm/@magenta/music@1.23.1/es6/core.js,npm/focus-visible@5,npm/html-midi-player@1.5.0"></script>
<midi-player src="data:audio/midi;base64,{b64}"
  sound-font="https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus"></midi-player>
"""))
        return None
    display(Audio(synth_midi(path, max_seconds=max_seconds), rate=16000))
    return None


def download(path: str) -> None:
    """Save a file to your computer (Colab) or tell you where it is (elsewhere)."""
    if IN_COLAB:
        from google.colab import files
        files.download(path)
    else:
        print(_t("saved_as", path=os.path.abspath(path)))


def download_zip(paths, name: str = "my_melody_files.zip") -> None:
    """Pack several files into one zip and download it (one click instead of many)."""
    import zipfile

    with zipfile.ZipFile(name, "w") as z:
        for p in paths:
            z.write(p)
    print(_t("packed"), ", ".join(paths))
    download(name)
