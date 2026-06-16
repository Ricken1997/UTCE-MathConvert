from dataclasses import dataclass, field
from typing import List


@dataclass
class OCHAnalysisResult:
    retained_differences: List[str] = field(default_factory=list)
    general_zero_candidates: List[str] = field(default_factory=list)
    residual_returns: List[str] = field(default_factory=list)
    observer_views: List[str] = field(default_factory=list)
    retranslation_candidates: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)


GENERAL_ZERO_MARKERS = [
    "ただし",
    "しかし",
    "一方で",
    "例外",
    "前提",
    "未検討",
    "省略",
    "曖昧",
    "不明",
    "触れていない",
    "考慮していない",
    "見落とし",
    "条件",
]

RESIDUAL_RETURN_MARKERS = [
    "矛盾",
    "違和感",
    "エラー",
    "失敗",
    "リジェクト",
    "誤答",
    "再発",
    "戻ってくる",
    "問題",
    "不整合",
    "破綻",
    "詰まる",
    "上手く行かない",
]


def split_lines(text: str) -> List[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def detect_retained_differences(lines: List[str]) -> List[str]:
    retained = []

    for line in lines:
        if any(marker in line for marker in ["定義", "目的", "結論", "主張", "条件"]):
            retained.append(line)

    if not retained and lines:
        retained.append(lines[0])

    return retained


def detect_general_zero(lines: List[str]) -> List[str]:
    candidates = []

    for line in lines:
        if any(marker in line for marker in GENERAL_ZERO_MARKERS):
            candidates.append(line)

    return candidates


def detect_residual_returns(lines: List[str]) -> List[str]:
    residuals = []

    for line in lines:
        if any(marker in line for marker in RESIDUAL_RETURN_MARKERS):
            residuals.append(line)

    return residuals


def build_observer_views(
    general_zero_candidates: List[str],
    residual_returns: List[str],
) -> List[str]:
    views = []

    if general_zero_candidates:
        views.append(
            "査読者視点: 未処理の前提・省略・曖昧さが指摘対象になりうる。"
        )
        views.append(
            "読者視点: 説明されていない差異が理解の負荷として残る。"
        )

    if residual_returns:
        views.append(
            "開発者視点: エラーや不整合は、ゼロ化された条件が処理系に戻ってきた可能性がある。"
        )
        views.append(
            "教師視点: 誤答や反復ミスは、見落とされた条件の残差として読むことができる。"
        )

    if not views:
        views.append(
            "観測者視点: 現時点では大きな General Zero の回帰は明確ではない。"
        )

    return views


def analyze_by_observer(text: str, observer: str) -> str:
    result = analyze_och(text)

    report = []
    report.append(f"OCH Observer Mode: {observer}")
    report.append("")

    report.append(format_och_report(result))
    report.append("")
    report.append("Observer-Specific Focus")

    if observer == "査読者":
        report.append("- 未処理の前提、文献接続、過剰主張が残差として戻る可能性があります。")
    elif observer == "教師":
        report.append("- 誤答や反復ミスは、見落とされた条件や手順の General Zero として読めます。")
    elif observer == "開発者":
        report.append("- エラーや不具合は、処理系が前提としていた条件のゼロ化として読めます。")
    elif observer == "AI":
        report.append("- 応答不能や一般論化は、文脈・制約・安全性レイヤーの General Zero として読めます。")
    else:
        report.append("- 指定観測者に応じた General Zero と残差回帰を確認してください。")

    return "\n".join(report)


def build_retranslation_candidates(
    general_zero_candidates: List[str],
    residual_returns: List[str],
) -> List[str]:
    candidates = []

    for item in general_zero_candidates:
        candidates.append(
            f"再翻訳候補: 「{item}」を明示的な前提・条件・制約として再定義する。"
        )

    for item in residual_returns:
        candidates.append(
            f"再翻訳候補: 「{item}」を単なる失敗ではなく、構造的残差として分析する。"
        )

    if not candidates:
        candidates.append(
            "再翻訳候補: 入力全体を、保持された差異と省略された差異に分けて再読する。"
        )

    return candidates


def build_next_actions(
    general_zero_candidates: List[str],
    residual_returns: List[str],
) -> List[str]:
    actions = []

    if general_zero_candidates:
        actions.append(
            "General Zero 候補を、前提・条件・未処理論点として明文化する。"
        )

    if residual_returns:
        actions.append(
            "残差が戻ってきている箇所を、修正対象ではなく診断対象として切り出す。"
        )

    if not actions:
        actions.append(
            "入力をさらに長くし、未処理の差異・矛盾・反復ミスを検出する。"
        )

    return actions


def analyze_och(text: str) -> OCHAnalysisResult:
    lines = split_lines(text)

    retained = detect_retained_differences(lines)
    general_zero = detect_general_zero(lines)
    residuals = detect_residual_returns(lines)

    observer_views = build_observer_views(
        general_zero,
        residuals,
    )

    retranslation_candidates = build_retranslation_candidates(
        general_zero,
        residuals,
    )

    next_actions = build_next_actions(
        general_zero,
        residuals,
    )

    return OCHAnalysisResult(
        retained_differences=retained,
        general_zero_candidates=general_zero,
        residual_returns=residuals,
        observer_views=observer_views,
        retranslation_candidates=retranslation_candidates,
        next_actions=next_actions,
    )


def format_och_report(result: OCHAnalysisResult) -> str:
    sections = []

    sections.append("1. 保持されている差異")
    sections.extend(f"- {item}" for item in result.retained_differences)

    sections.append("\n2. General Zero 化されている差異")
    if result.general_zero_candidates:
        sections.extend(f"- {item}" for item in result.general_zero_candidates)
    else:
        sections.append("- 明確な General Zero 候補は検出されていません。")

    sections.append("\n3. 戻ってきている残差")
    if result.residual_returns:
        sections.extend(f"- {item}" for item in result.residual_returns)
    else:
        sections.append("- 明確な残差回帰は検出されていません。")

    sections.append("\n4. 観測者別の見え方")
    sections.extend(f"- {item}" for item in result.observer_views)

    sections.append("\n5. 再翻訳候補")
    sections.extend(f"- {item}" for item in result.retranslation_candidates)

    sections.append("\n6. 次の行動")
    sections.extend(f"- {item}" for item in result.next_actions)

    return "\n".join(sections)


if __name__ == "__main__":
    sample_text = """
目的: 入力された文章から未処理の差異を検出する。
ただし、観測者ごとの違いはまだ十分に考慮していない。
このため、査読者から前提が曖昧だと指摘される可能性がある。
結果として、同じ問題が再発し、上手く行かない。
"""

    result = analyze_och(sample_text)
    print(analyze_by_observer(sample_text, "査読者"))