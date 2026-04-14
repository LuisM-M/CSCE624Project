import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

INPUT_FILE = "analysis/data/processed/all_segmented_trials.csv"

NON_FEATURE_COLUMNS = [
    "participant_id",
    "session_id",
    "difficulty",
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


def run_logistic_regression(X_train, X_test, y_train, y_test):
    labels = sorted(y_train.unique())

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=10000, random_state=42))
    ])

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("\n=== Logistic Regression ===")
    print("Accuracy:", accuracy_score(y_test, preds))
    print("\nClassification Report:")
    print(classification_report(y_test, preds, labels=labels))
    print_confusion_matrix_with_labels(y_test, preds, labels)


def run_random_forest(X_train, X_test, y_train, y_test, feature_cols):
    labels = sorted(y_train.unique())

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42
    )

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("\n=== Random Forest ===")
    print("Accuracy:", accuracy_score(y_test, preds))
    print("\nClassification Report:")
    print(classification_report(y_test, preds, labels=labels))
    print_confusion_matrix_with_labels(y_test, preds, labels)

    importances = pd.Series(model.feature_importances_, index=feature_cols)
    importances = importances.sort_values(ascending=False)

    print("\nTop 10 Feature Importances:")
    print(importances.head(10))


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

    run_logistic_regression(X_train, X_test, y_train, y_test)
    run_random_forest(X_train, X_test, y_train, y_test, feature_cols)


if __name__ == "__main__":
    main()