import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adjust_function import heuristic_notes


def diff(status, ref_instr, tgt_instr):
    return {
        "status": status,
        "ref_instr": ref_instr,
        "tgt_instr": tgt_instr,
    }


class HeuristicNotesTest(unittest.TestCase):
    def test_recognizes_mov_global_layout_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "mov ax, [0x8f2a]", "mov ax, [0x9278]"),
                diff("DIFF_OP2", "mov dx, [0x8f2c]", "mov dx, [0x927a]"),
                diff("DIFF_OP1", "mov [0x976c], ax", "mov [0x9aba], ax"),
                diff("DIFF_OP1", "mov [0x976e], dx", "mov [0x9abc], dx"),
            ],
        )
        self.assertTrue(
            any("mov-shaped address/operand drifts" in note for note in notes),
            notes,
        )

    def test_recognizes_paired_ax_dx_copy_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "mov ax, [0x8f2a]", "mov ax, [0x9278]"),
                diff("DIFF_OP2", "mov dx, [0x8f2c]", "mov dx, [0x927a]"),
                diff("DIFF_OP1", "mov [0x976c], ax", "mov [0x9aba], ax"),
                diff("DIFF_OP1", "mov [0x976e], dx", "mov [0x9abc], dx"),
                diff("DIFF_OP1", "mov [0x894e], ax", "mov [0x8c9c], ax"),
            ],
        )
        self.assertTrue(
            any("repeated AX/DX copy block" in note for note in notes),
            notes,
        )

    def test_paired_ax_dx_copy_drift_does_not_fire_for_hard_focus(self):
        notes = heuristic_notes(
            "hard",
            {
                "relevant_record": {
                    "ref_instr": "call 0xe9ec",
                    "tgt_instr": "call 0x39bb",
                }
            },
            [
                diff("DIFF_OP2", "mov ax, [0x8f2a]", "mov ax, [0x9278]"),
                diff("DIFF_OP2", "mov dx, [0x8f2c]", "mov dx, [0x927a]"),
                diff("DIFF_OP1", "mov [0x976c], ax", "mov [0x9aba], ax"),
                diff("DIFF_OP1", "mov [0x976e], dx", "mov [0x9abc], dx"),
                diff("DIFF_OP1", "mov [0x894e], ax", "mov [0x8c9c], ax"),
            ],
        )
        self.assertFalse(
            any("repeated AX/DX copy block" in note for note in notes),
            notes,
        )

    def test_recognizes_one_value_fanout_store_block(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "mov ax, [0xa004]", "mov ax, [0xa352]"),
                diff("DIFF_OP1", "mov [0x52ce], ax", "mov [0x5332], ax"),
                diff("DIFF_OP1", "mov [0x52ec], ax", "mov [0x5350], ax"),
                diff("DIFF_OP1", "mov [0x530a], ax", "mov [0x536e], ax"),
                diff("DIFF_OP1", "mov [0x5328], ax", "mov [0x538c], ax"),
            ],
        )
        self.assertTrue(
            any("one-value fan-out store block" in note for note in notes),
            notes,
        )

    def test_fanout_does_not_mask_paired_ax_dx_case(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "mov ax, [0x8f2a]", "mov ax, [0x9278]"),
                diff("DIFF_OP2", "mov dx, [0x8f2c]", "mov dx, [0x927a]"),
                diff("DIFF_OP1", "mov [0x976c], ax", "mov [0x9aba], ax"),
                diff("DIFF_OP1", "mov [0x976e], dx", "mov [0x9abc], dx"),
                diff("DIFF_OP1", "mov [0x894e], ax", "mov [0x8c9c], ax"),
            ],
        )
        self.assertTrue(any("repeated AX/DX copy block" in note for note in notes), notes)
        self.assertFalse(any("one-value fan-out store block" in note for note in notes), notes)

    def test_recognizes_call_operand_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP1", "call far 0x228b0f9f", "call far 0x152e1003"),
                diff("DIFF_OP1", "mov [0x9cf0], al", "mov [0xa03e], al"),
                diff("DIFF_OP2", "mov si, [0x182]", "mov si, [0x1e6]"),
            ],
        )
        self.assertTrue(
            any("same-shaped call operand drift" in note for note in notes),
            notes,
        )

    def test_recognizes_prologue_stack_frame_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "sub sp, 0x6", "sub sp, 0x4"),
                diff("DIFF_OP1", "mov [0x9df8], ax", "mov [0xa146], ax"),
                diff("DIFF_OP1", "mov word [0x9df6], 0x0", "mov word [0xa144], 0x0"),
            ],
        )
        self.assertTrue(
            any("stack-frame size drift in the prologue" in note for note in notes),
            notes,
        )


if __name__ == "__main__":
    unittest.main()
