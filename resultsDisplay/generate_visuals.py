import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def generate_lr_confusion_matrix():
    """Generates the Stroke-Level Confusion Matrix for Logistic Regression"""
    print("Generating Logistic Regression Confusion Matrix...")
    participants = ['jared', 'johnny', 'luis', 'pratt', 'richard', 'vish', 'zach']
    
    # Data extracted from ExperimentResults.txt (Logistic Regression)
    cm_data = [
        [21, 11, 0, 0, 15, 1, 0],
        [10, 13, 7, 1, 12, 4, 1],
        [4, 2, 33, 3, 1, 5, 0],
        [2, 4, 11, 25, 1, 5, 0],
        [20, 1, 3, 1, 21, 2, 0],
        [6, 9, 13, 2, 1, 16, 1],
        [1, 0, 0, 0, 0, 0, 47]
    ]

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_data, annot=True, fmt='d', cmap='Blues', 
                xticklabels=participants, yticklabels=participants)
    plt.title('Logistic Regression Stroke-Level Confusion Matrix')
    plt.ylabel('Actual User')
    plt.xlabel('Predicted User')
    plt.tight_layout()
    plt.savefig('lr_confusion_matrix.png', dpi=300) # Saved with high resolution for slides
    plt.close()

def generate_lr_session_table():
    """Generates the Session-Level Confidence Table for Logistic Regression"""
    print("Generating Session Performance Table...")
    
    session_data = [
        ['jared_s3', 'Jared', '21 / 48', '43.8%'],
        ['johnny_s3', 'Johnny', '13 / 48', '27.1%'],
        ['luis_s3', 'Luis', '33 / 48', '68.8%'],
        ['pratt_s3', 'Pratt', '25 / 48', '52.1%'],
        ['richard_s3', 'Richard', '21 / 48', '43.8%'],
        ['vish_s3', 'Vish', '16 / 48', '33.3%'],
        ['zach_s3', 'Zach', '47 / 48', '97.9%']
    ]
    columns = ['Session ID', 'Predicted User', 'Leading Votes', 'Confidence']

    plt.figure(figsize=(8, 4))
    ax = plt.gca()
    ax.axis('off') # Hide axes for a clean table look
    
    table = plt.table(cellText=session_data, colLabels=columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.8)
    
    plt.title('Session Majority Vote Performance (Logistic Regression)', pad=20)
    plt.tight_layout()
    plt.savefig('lr_session_performance.png', dpi=300)
    plt.close()

def generate_feature_importance():
    """
    Generates the Feature Importance Chart.
    Note: Because your text file only had the explicit values for Random Forest, 
    this uses those values. If you want the exact Logistic Regression ones, 
    you'll need to extract them directly from the model as discussed previously!
    """
    print("Generating Feature Importance Chart...")
    features = {
        'velocity_std': 0.075043,
        'rubine_f10_total_abs_rotation': 0.071191,
        'mean_velocity': 0.063651,
        'rubine_f13_duration': 0.063020,
        'rubine_f11_total_sq_rotation': 0.060022,
        'num_points': 0.057571,
        'efficiency_ratio': 0.056433,
        'max_velocity': 0.051908,
        'rubine_f12_max_speed_sq': 0.047252,
        'rubine_f8_stroke_length': 0.042484
    }
    
    feat_df = pd.DataFrame(list(features.items()), columns=['Feature', 'Importance'])
    feat_df = feat_df.sort_values(by='Importance', ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(feat_df['Feature'], feat_df['Importance'], color='skyblue', edgecolor='black')
    plt.title('Top 10 Feature Importances')
    plt.xlabel('Importance Score')
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_lr_confusion_matrix()
    generate_lr_session_table()
    generate_feature_importance()
    print("Done! Check your folder for the generated .png files.")