"""
Tests for IndexedCollection base class.

Following kicad-sch-api pattern for collection management.
"""

import pytest
from typing import Optional
from dataclasses import dataclass
from kicad_pcb_api.collections.base import IndexedCollection


# Test dataclass for collection testing
@dataclass
class TestItem:
    """Simple test item with UUID."""
    uuid: str
    name: str
    value: int


class TestItemCollection(IndexedCollection[TestItem]):
    """Concrete implementation for testing."""

    def _get_item_uuid(self, item: TestItem) -> str:
        return item.uuid

    def _create_item(self, **kwargs) -> TestItem:
        return TestItem(**kwargs)

    def _build_additional_indexes(self) -> None:
        # Build name index for testing
        self._name_index = {
            item.name: i for i, item in enumerate(self._items)
        }


class TestIndexedCollectionBasics:
    """Test basic collection operations."""

    def test_create_empty_collection(self):
        """Test creating an empty collection."""
        collection = TestItemCollection()
        assert len(collection) == 0
        assert collection.is_modified is False

    def test_create_collection_with_items(self):
        """Test creating collection with initial items."""
        items = [
            TestItem("uuid1", "item1", 10),
            TestItem("uuid2", "item2", 20),
        ]
        collection = TestItemCollection(items)
        assert len(collection) == 2
        assert collection.is_modified is False

    def test_add_item(self):
        """Test adding an item to collection."""
        collection = TestItemCollection()
        item = TestItem("uuid1", "test", 42)

        result = collection.add(item)

        assert result == item
        assert len(collection) == 1
        assert collection.is_modified is True

    def test_add_duplicate_uuid_raises_error(self):
        """Test that adding duplicate UUID raises ValueError."""
        collection = TestItemCollection()
        item1 = TestItem("uuid1", "test1", 10)
        item2 = TestItem("uuid1", "test2", 20)  # Same UUID

        collection.add(item1)

        with pytest.raises(ValueError, match="already exists"):
            collection.add(item2)

    def test_get_item_by_uuid(self):
        """Test retrieving item by UUID."""
        collection = TestItemCollection()
        item = TestItem("uuid1", "test", 42)
        collection.add(item)

        retrieved = collection.get("uuid1")

        assert retrieved == item
        assert retrieved.name == "test"
        assert retrieved.value == 42

    def test_get_nonexistent_uuid_returns_none(self):
        """Test that getting nonexistent UUID returns None."""
        collection = TestItemCollection()

        result = collection.get("nonexistent")

        assert result is None

    def test_remove_item_by_uuid(self):
        """Test removing item by UUID string."""
        collection = TestItemCollection()
        item = TestItem("uuid1", "test", 42)
        collection.add(item)

        removed = collection.remove("uuid1")

        assert removed is True
        assert len(collection) == 0
        assert collection.is_modified is True

    def test_remove_item_by_instance(self):
        """Test removing item by instance."""
        collection = TestItemCollection()
        item = TestItem("uuid1", "test", 42)
        collection.add(item)

        removed = collection.remove(item)

        assert removed is True
        assert len(collection) == 0

    def test_remove_nonexistent_item_returns_false(self):
        """Test that removing nonexistent item returns False."""
        collection = TestItemCollection()

        removed = collection.remove("nonexistent")

        assert removed is False

    def test_clear_collection(self):
        """Test clearing all items from collection."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "test1", 10))
        collection.add(TestItem("uuid2", "test2", 20))

        collection.clear()

        assert len(collection) == 0
        assert collection.is_modified is True


class TestIndexedCollectionIteration:
    """Test iteration and access patterns."""

    def test_iterate_over_collection(self):
        """Test iterating over collection items."""
        collection = TestItemCollection()
        items = [
            TestItem("uuid1", "item1", 10),
            TestItem("uuid2", "item2", 20),
            TestItem("uuid3", "item3", 30),
        ]
        for item in items:
            collection.add(item)

        result = list(collection)

        assert result == items

    def test_contains_by_uuid(self):
        """Test checking if UUID is in collection."""
        collection = TestItemCollection()
        item = TestItem("uuid1", "test", 42)
        collection.add(item)

        assert "uuid1" in collection
        assert "nonexistent" not in collection

    def test_contains_by_instance(self):
        """Test checking if item instance is in collection."""
        collection = TestItemCollection()
        item = TestItem("uuid1", "test", 42)
        other_item = TestItem("uuid2", "other", 99)
        collection.add(item)

        assert item in collection
        assert other_item not in collection

    def test_getitem_by_index(self):
        """Test accessing items by index."""
        collection = TestItemCollection()
        items = [
            TestItem("uuid1", "item1", 10),
            TestItem("uuid2", "item2", 20),
        ]
        for item in items:
            collection.add(item)

        assert collection[0] == items[0]
        assert collection[1] == items[1]


class TestIndexedCollectionFiltering:
    """Test filtering and search operations."""

    def test_find_with_predicate(self):
        """Test finding items with predicate function."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "item1", 10))
        collection.add(TestItem("uuid2", "item2", 20))
        collection.add(TestItem("uuid3", "item3", 30))

        result = collection.find(lambda item: item.value > 15)

        assert len(result) == 2
        assert result[0].value == 20
        assert result[1].value == 30

    def test_filter_by_criteria(self):
        """Test filtering by attribute criteria."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "test", 10))
        collection.add(TestItem("uuid2", "test", 20))
        collection.add(TestItem("uuid3", "other", 30))

        result = collection.filter(name="test")

        assert len(result) == 2
        assert result[0].name == "test"
        assert result[1].name == "test"

    def test_filter_multiple_criteria(self):
        """Test filtering with multiple criteria."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "test", 10))
        collection.add(TestItem("uuid2", "test", 20))
        collection.add(TestItem("uuid3", "other", 10))

        result = collection.filter(name="test", value=10)

        assert len(result) == 1
        assert result[0].uuid == "uuid1"


class TestIndexedCollectionIndexing:
    """Test index management and rebuilding."""

    def test_indexes_built_lazily(self):
        """Test that indexes are built lazily on first access."""
        collection = TestItemCollection()
        item = TestItem("uuid1", "test", 42)
        collection.add(item)

        # Indexes should be dirty
        assert collection._dirty_indexes is True

        # Access should trigger rebuild
        _ = collection.get("uuid1")

        assert collection._dirty_indexes is False

    def test_indexes_rebuilt_after_modification(self):
        """Test that indexes are rebuilt after modifications."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "test1", 10))
        collection.get("uuid1")  # Trigger index build

        # Add another item
        collection.add(TestItem("uuid2", "test2", 20))

        # Indexes should be dirty again
        assert collection._dirty_indexes is True

        # Should still work correctly
        item = collection.get("uuid2")
        assert item.name == "test2"

    def test_additional_indexes_built(self):
        """Test that subclass additional indexes are built."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "test", 42))

        # Trigger index build
        collection.get("uuid1")

        # Check name index was built
        assert hasattr(collection, '_name_index')
        assert "test" in collection._name_index


class TestIndexedCollectionStatistics:
    """Test collection statistics and debugging."""

    def test_get_statistics(self):
        """Test getting collection statistics."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "test1", 10))
        collection.add(TestItem("uuid2", "test2", 20))

        stats = collection.get_statistics()

        assert stats["item_count"] == 2
        assert stats["uuid_index_size"] == 2
        assert stats["modified"] is True
        assert stats["collection_type"] == "TestItemCollection"

    def test_mark_clean(self):
        """Test marking collection as clean."""
        collection = TestItemCollection()
        collection.add(TestItem("uuid1", "test", 42))

        assert collection.is_modified is True

        collection.mark_clean()

        assert collection.is_modified is False


class TestIndexedCollectionEdgeCases:
    """Test edge cases and error conditions."""

    def test_remove_from_empty_collection(self):
        """Test removing from empty collection."""
        collection = TestItemCollection()

        result = collection.remove("uuid1")

        assert result is False

    def test_multiple_add_remove_cycles(self):
        """Test multiple add/remove cycles."""
        collection = TestItemCollection()

        # Add, remove, add again
        item1 = TestItem("uuid1", "test", 42)
        collection.add(item1)
        collection.remove("uuid1")
        collection.add(item1)

        assert len(collection) == 1
        assert collection.get("uuid1") == item1

    def test_large_collection_performance(self):
        """Test performance with larger collection."""
        collection = TestItemCollection()

        # Add 1000 items
        for i in range(1000):
            collection.add(TestItem(f"uuid{i}", f"item{i}", i))

        # Access should be fast (O(1))
        item = collection.get("uuid500")
        assert item.name == "item500"
        assert item.value == 500

        # Filter should work
        high_values = collection.find(lambda item: item.value > 900)
        assert len(high_values) == 99
