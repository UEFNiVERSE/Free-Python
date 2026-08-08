"""Tests for the post-merge safety-fix batch:

1. undo_verse_edits() must never clobber hand edits made after apply
   (skip-if-modified via post_hashes, plus a pre-undo snapshot of every
   file it does restore).
2. build_verse_edits() must never rewrite the using-statement of a folder
   that was not fully vacated (occupied_folders).
3. undo()'s confirm dialog must fail CLOSED when the dialog call raises,
   matching apply's gate-2 semantics.
4. apply_verse_edits() must preserve a file's existing line endings
   (newline="" round-trip: LF stays LF, CRLF stays CRLF).
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import helpers
import mock_unreal


def asset(path, class_name):
    folder, name = path.rsplit("/", 1)
    return {"path": path, "name": name, "folder": folder, "class_name": class_name}


class VerseUndoHandEditProtectionTests(unittest.TestCase):
    def setUp(self):
        self.sortilege = helpers.load_sortilege()
        self.tmp_dir = tempfile.mkdtemp(prefix="sortilege_safety_files_")
        self.log_dir = tempfile.mkdtemp(prefix="sortilege_safety_logs_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        shutil.rmtree(self.log_dir, ignore_errors=True)

    def _write(self, relpath, content):
        full = os.path.join(self.tmp_dir, relpath)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        return full

    def _apply_one_edit(self, verse_file):
        move = {"path": "/PremFN_1v1/Stuff/T_Hex",
                "dest_path": "/PremFN_1v1/Textures/T_Hex",
                "dest_folder": "/PremFN_1v1/Textures"}
        edits = self.sortilege.build_verse_edits(
            [move], [verse_file], ["/PremFN_1v1"])
        self.assertTrue(edits)
        return self.sortilege.apply_verse_edits(edits, self.log_dir)

    def test_hand_edited_file_is_skipped_not_clobbered(self):
        verse_file = self._write("a.verse", "MyHex := Stuff.T_Hex\n")
        apply_result = self._apply_one_edit(verse_file)
        self.assertEqual(apply_result["failed"], [])

        # The exact workflow the report recommends: the user hand-fixes
        # the file after apply...
        hand_edited = "MyHex := Textures.T_Hex # hand-tuned after apply\n"
        with open(verse_file, "w", encoding="utf-8") as f:
            f.write(hand_edited)

        undo_result = self.sortilege.undo_verse_edits(apply_result["backup_index"])

        # ...and undo must keep their version, not silently revert it.
        self.assertEqual(undo_result["skipped_modified"], [verse_file])
        self.assertEqual(undo_result["restored"], [])
        self.assertEqual(undo_result["failed"], [])
        with open(verse_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), hand_edited)

    def test_unmodified_file_still_restores_and_is_snapshotted_first(self):
        original = "MyHex := Stuff.T_Hex\n"
        verse_file = self._write("a.verse", original)
        apply_result = self._apply_one_edit(verse_file)
        with open(verse_file, "r", encoding="utf-8") as f:
            post_apply = f.read()
        self.assertNotEqual(post_apply, original)

        undo_result = self.sortilege.undo_verse_edits(apply_result["backup_index"])

        self.assertEqual(undo_result["restored"], [verse_file])
        self.assertEqual(undo_result["skipped_modified"], [])
        with open(verse_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), original)

        # The overwritten (post-apply) content must be recoverable from
        # the pre-undo snapshot folder.
        snap_dir = undo_result["pre_undo_backup_dir"]
        self.assertIsNotNone(snap_dir)
        snap_files = [os.path.join(snap_dir, n) for n in os.listdir(snap_dir)]
        self.assertEqual(len(snap_files), 1)
        with open(snap_files[0], "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), post_apply)

    def test_v1_index_without_hashes_still_restores_with_snapshot(self):
        # An index written by the previous version has no post_hashes:
        # restore proceeds for every file (old behavior), but the
        # pre-undo snapshot safety net still applies.
        verse_file = self._write("a.verse", "MyHex := Stuff.T_Hex\n")
        apply_result = self._apply_one_edit(verse_file)
        index_path = apply_result["backup_index"]
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.pop("post_hashes", None)
        data["version"] = 1
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        with open(verse_file, "w", encoding="utf-8") as f:
            f.write("hand edit that a v1 index cannot detect\n")

        undo_result = self.sortilege.undo_verse_edits(index_path)

        self.assertEqual(undo_result["restored"], [verse_file])
        self.assertIsNotNone(undo_result["pre_undo_backup_dir"])
        snap_dir = undo_result["pre_undo_backup_dir"]
        snap_files = os.listdir(snap_dir)
        self.assertEqual(len(snap_files), 1)
        with open(os.path.join(snap_dir, snap_files[0]), "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "hand edit that a v1 index cannot detect\n")


class LineEndingPreservationTests(unittest.TestCase):
    def setUp(self):
        self.sortilege = helpers.load_sortilege()
        self.tmp_dir = tempfile.mkdtemp(prefix="sortilege_newline_files_")
        self.log_dir = tempfile.mkdtemp(prefix="sortilege_newline_logs_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        shutil.rmtree(self.log_dir, ignore_errors=True)

    def _apply_to_bytes(self, raw_bytes):
        verse_file = os.path.join(self.tmp_dir, "a.verse")
        with open(verse_file, "wb") as f:
            f.write(raw_bytes)
        move = {"path": "/PremFN_1v1/Stuff/T_Hex",
                "dest_path": "/PremFN_1v1/Textures/T_Hex",
                "dest_folder": "/PremFN_1v1/Textures"}
        edits = self.sortilege.build_verse_edits(
            [move], [verse_file], ["/PremFN_1v1"])
        self.assertTrue(edits)
        self.sortilege.apply_verse_edits(edits, self.log_dir)
        with open(verse_file, "rb") as f:
            return f.read()

    def test_lf_file_stays_lf(self):
        out = self._apply_to_bytes(b"MyHex := Stuff.T_Hex\nOther := 1\n")
        self.assertNotIn(b"\r", out)
        self.assertIn(b"Textures.T_Hex\n", out)

    def test_crlf_file_stays_crlf(self):
        out = self._apply_to_bytes(b"MyHex := Stuff.T_Hex\r\nOther := 1\r\n")
        self.assertEqual(out.count(b"\r\n"), 2)
        self.assertIn(b"Textures.T_Hex\r\n", out)


class UsingRewriteVacancyTests(unittest.TestCase):
    def setUp(self):
        self.sortilege = helpers.load_sortilege()
        self.tmp_dir = tempfile.mkdtemp(prefix="sortilege_using_files_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write(self, relpath, content):
        full = os.path.join(self.tmp_dir, relpath)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        return full

    MOVES = [
        {"path": "/PremFN_1v1/Kit/RockA", "dest_path": "/PremFN_1v1/Meshes/RockA",
         "dest_folder": "/PremFN_1v1/Meshes"},
        {"path": "/PremFN_1v1/Kit/RockB", "dest_path": "/PremFN_1v1/Meshes/RockB",
         "dest_folder": "/PremFN_1v1/Meshes"},
    ]

    def test_fully_vacated_folder_gets_using_rewrite(self):
        verse_file = self._write("a.verse", "using { /PremFN_1v1/Kit }\n")
        edits = self.sortilege.build_verse_edits(
            self.MOVES, [verse_file], ["/PremFN_1v1"], occupied_folders=set())
        using_edits = [e for e in edits if e["kind"] == "using"]
        self.assertEqual(len(using_edits), 1)
        self.assertIn("/PremFN_1v1/Meshes", using_edits[0]["new_line"])

    def test_occupied_folder_using_statement_is_left_alone(self):
        # Same moves, but something (say, a protected device asset)
        # stayed behind in /PremFN_1v1/Kit -- rewriting the using line
        # would break every reference to it.
        verse_file = self._write("a.verse", "using { /PremFN_1v1/Kit }\n")
        edits = self.sortilege.build_verse_edits(
            self.MOVES, [verse_file], ["/PremFN_1v1"],
            occupied_folders={"/PremFN_1v1/Kit"})
        using_edits = [e for e in edits if e["kind"] == "using"]
        self.assertEqual(using_edits, [])

    def test_plan_marks_skipped_asset_folders_occupied(self):
        # End-to-end through build_plan(): a protected/skipped asset in
        # the same folder as the moves must suppress the using rewrite.
        verse_file = self._write("a.verse", "using { /Game/Kit }\n")
        assets = [asset("/Game/Kit/RockA", "StaticMesh"),
                  asset("/Game/Kit/RockB", "StaticMesh"),
                  asset("/Game/Kit/MyDevice", "VerseDevice")]
        for a in assets:
            mock_unreal.add_asset(a["path"], a["class_name"])
        config = dict(self.sortilege.CONFIG)
        config["VERSE_SEARCH_DIR"] = self.tmp_dir
        plan = self.sortilege.build_plan(
            assets, config, self.sortilege.probe_capabilities())

        # Prove the verse scan actually ran (guards against this test
        # passing trivially if the config key or scan wiring changes).
        self.assertEqual(plan.get("verse_files_count"), 1)

        moved_paths = {m["path"] for m in plan["moves"]}
        skipped_paths = {s["path"] for s in plan["skips"]}
        self.assertIn("/Game/Kit/MyDevice", skipped_paths)
        self.assertTrue({"/Game/Kit/RockA", "/Game/Kit/RockB"} <= moved_paths)

        using_edits = [e for e in plan.get("verse_edits", [])
                       if e["kind"] == "using"]
        self.assertEqual(using_edits, [])


class UndoDialogFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.sortilege = helpers.load_sortilege()
        self.tmp_dir = tempfile.mkdtemp(prefix="sortilege_dialog_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_undo_blocks_when_dialog_raises(self):
        assets = [asset("/Game/Stuff/Rock", "StaticMesh")]
        mock_unreal.add_asset(assets[0]["path"], assets[0]["class_name"])
        plan = self.sortilege.build_plan(
            assets, dict(self.sortilege.CONFIG), self.sortilege.probe_capabilities())
        caps = self.sortilege.probe_capabilities()
        self.assertTrue(caps.editor_dialog)
        undo_log = self.sortilege.UndoLog.begin(self.tmp_dir, plan)
        self.sortilege.execute_plan(plan, caps, undo_log)

        self.sortilege.CONFIG["I_UNDERSTAND_THIS_MODIFIES_MY_PROJECT"] = True

        def _raises(*_args, **_kwargs):
            raise RuntimeError("dialog exploded on this build")

        original = mock_unreal._EditorDialogImpl.show_message
        mock_unreal._EditorDialogImpl.show_message = staticmethod(_raises)
        try:
            result = self.sortilege.undo(undo_log.path, caps)
        finally:
            mock_unreal._EditorDialogImpl.show_message = original

        # Fail closed: blocked, and nothing restored.
        self.assertEqual(result["moved"], [])
        self.assertEqual(result.get("blocked"), "dialog unavailable")
        state = mock_unreal.get_state()
        self.assertIn("/Game/Meshes/Rock", state["assets"])
        self.assertNotIn("/Game/Stuff/Rock", state["assets"])


if __name__ == "__main__":
    unittest.main()
