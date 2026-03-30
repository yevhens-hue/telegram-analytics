import json
import logging
from datetime import datetime, timedelta
from db_utils import get_connection, get_placeholder, save_backtest_result

logger = logging.getLogger(__name__)


def run_backtest(days_back: int = 30, prediction_horizon: int = 7):
    """
    Compare past prediction_7d values with actual positions.
    Returns accuracy metrics for each app.
    """
    p = get_placeholder()
    today = datetime.now()
    results = []

    with get_connection() as conn:
        c = conn.cursor()

        cutoff = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
        c.execute(
            f"SELECT app_name, date, position, prediction_7d FROM app_analytics WHERE date >= {p} AND prediction_7d IS NOT NULL ORDER BY date",
            (cutoff,),
        )
        predictions = c.fetchall()

        for app_name, pred_date, pred_position, predicted_7d in predictions:
            future_date = (datetime.strptime(pred_date, "%Y-%m-%d") + timedelta(days=prediction_horizon)).strftime("%Y-%m-%d")

            c.execute(
                f"SELECT position FROM app_analytics WHERE app_name = {p} AND date = {p}",
                (app_name, future_date),
            )
            actual_row = c.fetchone()

            if actual_row:
                actual_position = actual_row[0]
                error = abs(predicted_7d - actual_position)
                direction_correct = (
                    (predicted_7d < pred_position and actual_position < pred_position) or
                    (predicted_7d > pred_position and actual_position > pred_position) or
                    (predicted_7d == pred_position and actual_position == pred_position)
                )
                results.append({
                    "app_name": app_name,
                    "prediction_date": pred_date,
                    "predicted_position": predicted_7d,
                    "actual_position": actual_position,
                    "error": error,
                    "direction_correct": direction_correct,
                })

    if not results:
        logger.warning("Нет данных для бэктестинга. Нужно минимум %d дней исторических данных.", prediction_horizon)
        return None

    total = len(results)
    correct_direction = sum(1 for r in results if r["direction_correct"])
    avg_error = sum(r["error"] for r in results) / total
    max_error = max(r["error"] for r in results)
    min_error = min(r["error"] for r in results)

    per_app = {}
    for r in results:
        name = r["app_name"]
        if name not in per_app:
            per_app[name] = {"total": 0, "correct": 0, "errors": []}
        per_app[name]["total"] += 1
        if r["direction_correct"]:
            per_app[name]["correct"] += 1
        per_app[name]["errors"].append(r["error"])

    report = {
        "period_days": days_back,
        "prediction_horizon": prediction_horizon,
        "total_predictions": total,
        "direction_accuracy_pct": round(correct_direction / total * 100, 1),
        "avg_position_error": round(avg_error, 2),
        "max_position_error": max_error,
        "min_position_error": min_error,
        "per_app": {
            name: {
                "predictions": data["total"],
                "direction_accuracy_pct": round(data["correct"] / data["total"] * 100, 1),
                "avg_error": round(sum(data["errors"]) / len(data["errors"]), 2),
            }
            for name, data in per_app.items()
        },
    }

    logger.info("Бэктестинг завершён: %d прогнозов, точность направления: %.1f%%, средняя ошибка: %.2f позиций",
                total, report["direction_accuracy_pct"], avg_error)

    save_backtest_result(
        days_back,
        total,
        report["direction_accuracy_pct"],
        report["avg_position_error"],
        json.dumps(report, ensure_ascii=False)
    )

    return report


def get_backtest_summary(days_back: int = 30) -> str:
    """Returns a human-readable backtest summary."""
    report = run_backtest(days_back)
    if not report:
        return "Недостаточно данных для бэктестинга."

    lines = [
        f"📊 Backtest Report ({report['period_days']} дней, прогноз на {report['prediction_horizon']}д)",
        f"Всего прогнозов: {report['total_predictions']}",
        f"Точность направления: {report['direction_accuracy_pct']}%",
        f"Средняя ошибка позиции: {report['avg_position_error']}",
        f"Мин/Макс ошибка: {report['min_position_error']}/{report['max_position_error']}",
        "",
        "По приложениям:",
    ]
    for name, data in report["per_app"].items():
        lines.append(f"  {name}: {data['direction_accuracy_pct']}% направление, средн. ошибка {data['avg_error']}")

    return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(get_backtest_summary())
