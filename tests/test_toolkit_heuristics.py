import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adjust_function import add_shape_notes, heuristic_notes


def diff(status, ref_instr, tgt_instr):
    return {
        "status": status,
        "ref_instr": ref_instr,
        "tgt_instr": tgt_instr,
    }


def lst(offset, instruction):
    return {
        "offset": offset,
        "text": f"seg000:{offset:04x} {instruction}",
    }


def cod(address, instruction):
    return {
        "address": address,
        "instruction": instruction,
        "mnemonic": instruction.split()[0].lower(),
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

    def test_recognizes_far_pointer_reload_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "les bx, [0x9df6]", "les bx, [0xa144]"),
                diff("DIFF_OP1", "call 0x688", "call 0x349c"),
                diff("DIFF_OP2", "les bx, [0x9df6]", "les bx, [0xa144]"),
                diff("DIFF_OP1", "call 0x688", "call 0x349c"),
                diff("DIFF_OP2", "les bx, [0x9df6]", "les bx, [0xa144]"),
            ],
        )
        self.assertTrue(
            any("repeated far-pointer reloads" in note for note in notes),
            notes,
        )

    def test_recognizes_repeated_helper_call_setup_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP1", "cmp word [0x9760], 0x0", "cmp word [0x9aae], 0x0"),
                diff("DIFF_OP1", "push [0x6424]", "push [0x6488]"),
                diff("DIFF_OP1", "push [0x6426]", "push [0x648a]"),
                diff("DIFF_OP1", "call 0xeb00", "call 0x5126"),
                diff("DIFF_OP1", "push [0x6424]", "push [0x6488]"),
                diff("DIFF_OP1", "push [0x6426]", "push [0x648a]"),
                diff("DIFF_OP1", "call 0xeb00", "call 0x5126"),
            ],
        )
        self.assertTrue(
            any("repeat a helper-call setup pattern" in note for note in notes),
            notes,
        )

    def test_recognizes_literal_load_and_jump_tail_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "mov ax, 0x5f7c", "mov ax, 0x5fe0"),
                diff("DIFF_OP1", "jmp 0xdf80", "jmp 0x38cf"),
                diff("DIFF_OP2", "mov ax, 0x5f8c", "mov ax, 0x5ff0"),
                diff("DIFF_OP1", "jmp 0xdf80", "jmp 0x38cf"),
                diff("DIFF_OP2", "mov ax, 0x5fa7", "mov ax, 0x600b"),
                diff("DIFF_OP1", "jmp 0xdf80", "jmp 0x38cf"),
            ],
        )
        self.assertTrue(
            any("literal-load and jump-to-shared-tail blocks" in note for note in notes),
            notes,
        )

    def test_recognizes_constant_table_register_setup_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "mov dx, 0x43b6", "mov dx, 0x441a"),
                diff("DIFF_OP1", "cmp byte [0x18e7], 0x2", "cmp byte [0x194b], 0x2"),
                diff("DIFF_OP2", "mov si, 0x4866", "mov si, 0x48ca"),
                diff("DIFF_OP2", "mov di, 0x44d6", "mov di, 0x453a"),
                diff("DIFF_OP2", "mov dx, 0x44a6", "mov dx, 0x450a"),
            ],
        )
        self.assertTrue(
            any("constant table/register setup" in note for note in notes),
            notes,
        )

    def test_recognizes_shift_plus_zero_extend_scale_setup_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP2", "mov ax, [0x581e]", "mov ax, [0x5882]"),
                diff("DIFF_OP2", "mov cl, 0x7", "mov cl, 0x7"),
                diff("DIFF_OP1", "shr ax, cl", "shr ax, cl"),
                diff("DIFF_OP2", "add ah, 0x4", "add ah, 0x4"),
                diff("DIFF_OP1", "sub cx, cx", "sub cx, cx"),
                diff("DIFF_OP1", "push cx", "push cx"),
                diff("DIFF_OP1", "push ax", "push ax"),
                diff("DIFF_OP1", "call 0xecb0", "call 0x5338"),
                diff("DIFF_OP2", "mov ax, [0x5820]", "mov ax, [0x5884]"),
                diff("DIFF_OP2", "mov cl, 0x6", "mov cl, 0x6"),
                diff("DIFF_OP1", "shr ax, cl", "shr ax, cl"),
                diff("DIFF_OP2", "add ah, 0x4", "add ah, 0x4"),
                diff("DIFF_OP1", "sub cx, cx", "sub cx, cx"),
                diff("DIFF_OP1", "push cx", "push cx"),
                diff("DIFF_OP1", "push ax", "push ax"),
                diff("DIFF_OP1", "call 0xecb0", "call 0x5338"),
            ],
        )
        self.assertTrue(
            any("shift-plus-zero-extend scale setup" in note for note in notes),
            notes,
        )

    def test_scale_setup_drift_does_not_fire_for_generic_push_call_setup(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP1", "push [0x6424]", "push [0x6488]"),
                diff("DIFF_OP1", "push [0x6426]", "push [0x648a]"),
                diff("DIFF_OP1", "call 0xeb00", "call 0x5126"),
                diff("DIFF_OP1", "push [0x6424]", "push [0x6488]"),
                diff("DIFF_OP1", "push [0x6426]", "push [0x648a]"),
                diff("DIFF_OP1", "call 0xeb00", "call 0x5126"),
            ],
        )
        self.assertFalse(
            any("shift-plus-zero-extend scale setup" in note for note in notes),
            notes,
        )

    def test_add_shape_notes_recognizes_spilled_scale_factor(self):
        notes = add_shape_notes(
            [],
            [
                lst(0x4B1C, "mov ax, [0x581e]"),
                lst(0x4B1F, "mov cl, 0x7"),
                lst(0x4B21, "shr ax, cl"),
                lst(0x4B23, "add ah, 0x4"),
                lst(0x4B26, "sub cx, cx"),
                lst(0x4B28, "push cx"),
                lst(0x4B29, "push ax"),
            ],
            {
                "items": [
                    cod(0x1898, "mov ax, [0x5882]"),
                    cod(0x189b, "mov cl, 0x7"),
                    cod(0x189d, "shr ax, cl"),
                    cod(0x189f, "add ah, 0x4"),
                    cod(0x18a2, "mov [bp-0x10], ax"),
                    cod(0x18a5, "mov ax, [bp-0x30]"),
                    cod(0x18a8, "cwd"),
                ]
            },
        )
        self.assertTrue(
            any("spills a computed scale factor" in note for note in notes),
            notes,
        )

    def test_recognizes_repeated_bare_helper_call_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP1", "call far 0x228b0ebe", "call far 0x152e0f22"),
                diff("DIFF_OP1", "call far 0x228b0ebe", "call far 0x152e0f22"),
                diff("DIFF_OP1", "call far 0x228b1035", "call far 0x152e1099"),
                diff("DIFF_OP2", "les bx, [0x9df6]", "les bx, [0xa144]"),
                diff("DIFF_OP1", "call far 0x228b1035", "call far 0x152e1099"),
            ],
        )
        self.assertTrue(
            any("repeat the same helper-call shape" in note for note in notes),
            notes,
        )

    def test_recognizes_callback_vector_install_drift(self):
        notes = heuristic_notes(
            "soft",
            None,
            [
                diff("DIFF_OP1", "mov word [0x504a], 0x1", "mov word [0x50ae], 0x1"),
                diff("DIFF_OP1", "mov word [0x5054], 0x1", "mov word [0x50b8], 0x1"),
                diff("DIFF_OP1", "call 0x3df2", "call 0x365a"),
                diff("DIFF_OP1", "mov cs:[0x3d67], bx", "mov cs:[0x3655], bx"),
                diff("DIFF_OP1", "mov cs:[0x3d69], es", "mov cs:[0x3657], es"),
                diff("DIFF_OP2", "lds dx, cs:[0x3d01]", "lds dx, cs:[0x3646]"),
            ],
        )
        self.assertTrue(
            any("callback/vector install setup" in note for note in notes),
            notes,
        )


class ShapeNotesTest(unittest.TestCase):
    def test_recognizes_branch_signedness_drift(self):
        notes = add_shape_notes(
            [],
            [
                lst(0x100, "cmp ax, 0x4e"),
                lst(0x103, "jl short loc_1"),
            ],
            {
                "items": [
                    cod(0x200, "cmp ax, 0x4e"),
                    cod(0x203, "jb $L1"),
                ]
            },
        )
        self.assertTrue(any("Branch signedness drift" in note for note in notes), notes)

    def test_recognizes_zero_check_materialization_drift(self):
        notes = add_shape_notes(
            [],
            [
                lst(0x120, "cmp ax, 0"),
                lst(0x123, "jz short loc_2"),
            ],
            {
                "items": [
                    cod(0x220, "test ax, ax"),
                    cod(0x222, "jz $L2"),
                ]
            },
        )
        self.assertTrue(
            any("Zero/nonzero condition materialization drift" in note for note in notes),
            notes,
        )

    def test_recognizes_extra_mov_pressure(self):
        notes = add_shape_notes(
            [],
            [
                lst(0x140, "mov ax, [0x1000]"),
                lst(0x144, "cmp ax, 0"),
                lst(0x147, "jz short loc_3"),
                lst(0x144, "call 0x2000"),
            ],
            {
                "items": [
                    cod(0x240, "mov ax, [0x1000]"),
                    cod(0x244, "mov dx, ax"),
                    cod(0x246, "mov bx, dx"),
                    cod(0x248, "call 0x2000"),
                ]
            },
        )
        self.assertTrue(any("extra mov instructions" in note for note in notes), notes)

    def test_recognizes_extra_push_pressure(self):
        notes = add_shape_notes(
            [],
            [
                lst(0x160, "push ax"),
                lst(0x162, "cmp bx, 0"),
                lst(0x165, "jz short loc_4"),
                lst(0x168, "call 0x2200"),
            ],
            {
                "items": [
                    cod(0x260, "push ax"),
                    cod(0x262, "push bx"),
                    cod(0x264, "push cx"),
                    cod(0x266, "call 0x2200"),
                ]
            },
        )
        self.assertTrue(any("materializes more stack arguments" in note for note in notes), notes)

    def test_recognizes_signed_division_drift(self):
        notes = add_shape_notes(
            [],
            [
                lst(0x180, "xor dx, dx"),
                lst(0x182, "div cx"),
            ],
            {
                "items": [
                    cod(0x280, "cwd"),
                    cod(0x281, "idiv cx"),
                ]
            },
        )
        self.assertTrue(any("signed division/sign-extension" in note for note in notes), notes)


if __name__ == "__main__":
    unittest.main()
