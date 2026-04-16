import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from collections import Counter


INPUT_FILE = "analysis/data/processed/all_segmented_trials.csv"

NON_FEATURE_COLUMNS = [
    "participant_id",
    "session_id",
    "difficulty",
    "trial_index",
    "target_index",
]


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def make_train_test_split(df: pd.DataFrame):
    train_df = df[df["session_id"].isin(["s1", "s2"])].copy()
    test_df = df[df["session_id"] == "s3"].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("Train or test split is empty. Check your session_id values.")

    feature_cols = [c for c in df.columns if c not in NON_FEATURE_COLUMNS]

    X_train = train_df[feature_cols]
    y_train = train_df["participant_id"]

    X_test = test_df[feature_cols]
    y_test = test_df["participant_id"]

    return train_df, test_df, X_train, X_test, y_train, y_test, feature_cols


def print_dataset_summary(train_df: pd.DataFrame, test_df: pd.DataFrame):
    print("\n=== Dataset Summary ===")
    print("Train rows:", len(train_df))
    print("Test rows:", len(test_df))

    print("\nTrain rows by participant:")
    print(train_df["participant_id"].value_counts().sort_index())

    print("\nTest rows by participant:")
    print(test_df["participant_id"].value_counts().sort_index())

    print("\nTrain rows by session:")
    print(train_df["session_id"].value_counts().sort_index())

    print("\nTest rows by session:")
    print(test_df["session_id"].value_counts().sort_index())


def print_confusion_matrix_with_labels(y_test, preds, labels):
    cm = confusion_matrix(y_test, preds, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)

    print("\nConfusion Matrix:")
    print(cm_df)


def evaluate_session_level(test_df: pd.DataFrame, preds, model_name: str):
    """
    Groups stroke-level predictions by true session and evaluates
    majority-vote session classification.

    Since session_id alone is not unique across participants
    (everyone has s1/s2/s3), we group by:
        (participant_id, session_id)
    """

    eval_df = test_df[["participant_id", "session_id"]].copy()
    eval_df["predicted_participant"] = preds

    grouped = eval_df.groupby(["participant_id", "session_id"])

    session_results = []
    correct_sessions = 0
    total_sessions = 0

    for (true_participant, session_id), group in grouped:
        vote_counts = Counter(group["predicted_participant"])
        predicted_participant = vote_counts.most_common(1)[0][0]

        is_correct = predicted_participant == true_participant
        if is_correct:
            correct_sessions += 1
        total_sessions += 1

        session_results.append({
            "true_participant": true_participant,
            "session_id": session_id,
            "predicted_participant": predicted_participant,
            "num_strokes": len(group),
            "vote_counts": dict(vote_counts),
            "correct": is_correct,
        })

    session_accuracy = correct_sessions / total_sessions if total_sessions > 0 else 0.0

    print(f"\n=== {model_name} Session-Level Majority Vote ===")
    print(f"Session Accuracy: {session_accuracy:.4f}")
    print("\nSession Predictions:")

    for result in session_results:
        print(
            f"{result['true_participant']}_{result['session_id']} "
            f"-> predicted {result['predicted_participant']} | "
            f"strokes={result['num_strokes']} | "
            f"votes={result['vote_counts']} | "
            f"correct={result['correct']}"
        )


def run_logistic_regression(X_train, X_test, y_train, y_test, test_df):
    labels = sorted(y_train.unique())

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=10000, random_state=42))
    ])

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("\n=== Logistic Regression ===")
    print("Stroke-Level Accuracy:", accuracy_score(y_test, preds))
    print("\nClassification Report:")
    print(classification_report(y_test, preds, labels=labels))
    print_confusion_matrix_with_labels(y_test, preds, labels)

    evaluate_session_level(test_df, preds, "Logistic Regression")


def run_random_forest(X_train, X_test, y_train, y_test, feature_cols, test_df):
    labels = sorted(y_train.unique())

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("\n=== Random Forest ===")
    print("Stroke-Level Accuracy:", accuracy_score(y_test, preds))
    print("\nClassification Report:")
    print(classification_report(y_test, preds, labels=labels))
    print_confusion_matrix_with_labels(y_test, preds, labels)

    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)

    print("\nTop 10 Feature Importances:")
    print(importances.head(10))

    evaluate_session_level(test_df, preds, "Random Forest")


def main():
    df = load_data(INPUT_FILE)

    print("Loaded rows:", len(df))
    print("Participants:", sorted(df["participant_id"].unique()))
    print("Sessions:", sorted(df["session_id"].unique()))

    train_df, test_df, X_train, X_test, y_train, y_test, feature_cols = make_train_test_split(df)

    print("Num features:", len(feature_cols))
    print("Feature columns:")
    print(feature_cols)

    print_dataset_summary(train_df, test_df)

    run_logistic_regression(X_train, X_test, y_train, y_test, test_df)
    run_random_forest(X_train, X_test, y_train, y_test, feature_cols, test_df)


if __name__ == "__main__":
    main()