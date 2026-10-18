#!/usr/bin/env python3
"""Unit tests for the marketplace's manifests and its skills' frontmatter.

Run from the repo root: python3 -m unittest discover -s tests
No dependencies beyond the standard library.

These are rules nothing else here enforces. `claude plugin validate` checks that
a manifest parses and that a plugin name is permitted, but it passes a skill
`description` well past the platform's 1024-character ceiling, and nothing
compares a plugin's own version against its `marketplace.json` entry. Both fail
where they are least visible: a description over the ceiling at claude.ai
ingestion rather than at validate, and a disagreeing version in a catalogue
nobody re-reads. Each case below names one plugin or skill at a time, so a
failure says which.
"""
import glob
import json
import os
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

# A plugin or skill name carrying either word is rejected — the CLI refuses the
# plugin, claude.ai's ingestion refuses the skill. ADR-010 records what that
# cost before it was known.
RESERVED_WORDS = ("claude", "anthropic")

NAME_MAX = 64
DESCRIPTION_MAX = 1024


def skills():
    """Every skill, as (plugin, skill, path)."""
    for path in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        yield path.parents[2].name, path.parent.name, path


def plugin_manifests():
    """Every plugin's own manifest, as (plugin, path, parsed)."""
    for path in sorted(ROOT.glob("plugins/*/.claude-plugin/plugin.json")):
        yield path.parents[1].name, path, json.loads(path.read_text(encoding="utf-8"))


def frontmatter(path):
    """A skill's frontmatter fields, read the way the loader does: a value is
    whatever follows `key: ` to the end of that line, and nowhere else."""
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    if match is None:
        return None, {}
    block = match.group(1)
    return block, dict(re.findall(r"^([A-Za-z0-9_-]+): (.*)$", block, re.M))


def catalogue():
    return {
        entry["name"]: entry
        for entry in json.loads(MARKETPLACE.read_text(encoding="utf-8"))["plugins"]
    }


class SkillFrontmatterTestCase(unittest.TestCase):
    def test_every_skill_declares_both_fields(self):
        for plugin, skill, path in skills():
            with self.subTest(skill=f"{plugin}/{skill}"):
                block, fields = frontmatter(path)
                self.assertIsNotNone(block, "no YAML frontmatter")
                self.assertIn("name", fields)
                self.assertIn("description", fields)

    def test_name_is_within_its_ceiling_and_charset(self):
        for plugin, skill, path in skills():
            with self.subTest(skill=f"{plugin}/{skill}"):
                name = frontmatter(path)[1].get("name", "")
                self.assertLessEqual(len(name), NAME_MAX, f"{len(name)} characters")
                self.assertRegex(name, r"^[a-z0-9-]+$")

    def test_name_matches_the_directory_it_sits_in(self):
        for plugin, skill, path in skills():
            with self.subTest(skill=f"{plugin}/{skill}"):
                self.assertEqual(frontmatter(path)[1].get("name"), skill)

    def test_description_is_non_empty_and_within_its_ceiling(self):
        for plugin, skill, path in skills():
            with self.subTest(skill=f"{plugin}/{skill}"):
                description = frontmatter(path)[1].get("description", "")
                self.assertTrue(description.strip(), "empty description")
                # Characters, not bytes: an em dash is one character and three
                # bytes, so counting bytes overstates every description here.
                self.assertLessEqual(
                    len(description), DESCRIPTION_MAX, f"{len(description)} characters",
                )

    def test_neither_field_carries_an_xml_tag(self):
        for plugin, skill, path in skills():
            with self.subTest(skill=f"{plugin}/{skill}"):
                fields = frontmatter(path)[1]
                for key in ("name", "description"):
                    self.assertNotRegex(fields.get(key, ""), r"<[A-Za-z/!?]")

    def test_neither_field_hides_a_colon_space(self):
        for plugin, skill, path in skills():
            with self.subTest(skill=f"{plugin}/{skill}"):
                block, fields = frontmatter(path)
                for key in ("name", "description"):
                    value = fields.get(key, "")
                    # An unquoted value containing ": " parses as a mapping and
                    # the frontmatter is dropped without complaint.
                    self.assertNotIn(": ", value)
                # A field spread over two lines would leave a continuation line.
                for line in (block or "").splitlines():
                    self.assertRegex(line, r"^[A-Za-z0-9_-]+: ")


class SkillNameTestCase(unittest.TestCase):
    def test_no_skill_name_carries_a_reserved_word(self):
        for plugin, skill, path in skills():
            with self.subTest(skill=f"{plugin}/{skill}"):
                name = frontmatter(path)[1].get("name", "")
                for word in RESERVED_WORDS:
                    self.assertNotIn(word, name)

    def test_no_plugin_name_carries_a_reserved_word(self):
        for plugin, path, manifest in plugin_manifests():
            with self.subTest(plugin=plugin):
                for word in RESERVED_WORDS:
                    self.assertNotIn(word, manifest["name"])


class ManifestTestCase(unittest.TestCase):
    def test_plugin_name_matches_its_directory(self):
        for plugin, path, manifest in plugin_manifests():
            with self.subTest(plugin=plugin):
                self.assertEqual(manifest["name"], plugin)

    def test_every_plugin_is_catalogued(self):
        listed = catalogue()
        for plugin, path, manifest in plugin_manifests():
            with self.subTest(plugin=plugin):
                self.assertIn(manifest["name"], listed)

    def test_every_catalogue_entry_has_a_plugin(self):
        for name, entry in catalogue().items():
            with self.subTest(plugin=name):
                self.assertTrue((ROOT / "plugins" / name).is_dir())
                self.assertEqual(entry.get("source"), f"./plugins/{name}")

    def test_versions_agree_with_the_catalogue(self):
        listed = catalogue()
        for plugin, path, manifest in plugin_manifests():
            with self.subTest(plugin=plugin):
                self.assertEqual(
                    manifest.get("version"),
                    listed.get(manifest["name"], {}).get("version"),
                    "plugin.json and marketplace.json disagree",
                )

    def test_descriptions_are_present_on_both_sides(self):
        listed = catalogue()
        for plugin, path, manifest in plugin_manifests():
            with self.subTest(plugin=plugin):
                # The two descriptions address different readers — the catalogue
                # blurb and the plugin's own — and 13 of the 16 here differ, so
                # they are required rather than compared.
                self.assertTrue(manifest.get("description", "").strip())
                self.assertTrue(
                    listed.get(manifest["name"], {}).get("description", "").strip(),
                    "the catalogue entry carries no description",
                )

    def test_declared_dependencies_exist(self):
        listed = catalogue()
        for plugin, path, manifest in plugin_manifests():
            for dependency in manifest.get("dependencies", []):
                name = dependency if isinstance(dependency, str) else dependency.get("name", "")
                with self.subTest(plugin=plugin, dependency=name):
                    self.assertIn(name.split("@")[0], listed)


if __name__ == "__main__":
    unittest.main()
