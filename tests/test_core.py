from pathlib import Path

from wechat_plotkit.extract import detect_libraries, infer_plot_types, recommend_template
from wechat_plotkit.input_loader import load_links_from_markdown
from wechat_plotkit.utils import normalize_url, slugify


def test_load_links_from_markdown(tmp_path: Path) -> None:
    path = tmp_path / "links.md"
    path.write_text(
        "https://mp.weixin.qq.com/s/a\n\nhttps://mp.weixin.qq.com/s/b\nhttps://mp.weixin.qq.com/s/a",
        encoding="utf-8",
    )
    assert load_links_from_markdown(path) == [
        "https://mp.weixin.qq.com/s/a",
        "https://mp.weixin.qq.com/s/b",
    ]


def test_slugify_keeps_chinese() -> None:
    assert slugify("顶刊 风格 Plot 001") == "顶刊-风格-plot-001"


def test_normalize_url_decodes_ampersand() -> None:
    assert normalize_url("https://a.com/x?x=1&amp;y=2") == "https://a.com/x?x=1&y=2"


def test_library_and_plot_inference() -> None:
    text = "import matplotlib.pyplot as plt\nimport seaborn as sns\nax.scatter(x, y)\nfig, ax = plt.subplots()"
    assert detect_libraries(text) == ["matplotlib", "seaborn"]
    assert "scatter" in infer_plot_types(text)
    assert recommend_template(["scatter"]) == "scatter"
