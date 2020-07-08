from _wagyu import RingManager


def test_basic() -> None:
    result = RingManager()

    assert not result.index
    assert not result.all_nodes
    assert not result.nodes
    assert not result.storage
    assert not result.hot_pixels
    assert not result.rings
    assert not result.children
