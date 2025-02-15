import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def create_impact_visualizations(df):
    # Impact Distribution Heatmap
    plt.figure(figsize=(15, 8))
    impact_cols = ['economicImpact', 'environmentalImpact', 'socialImpact']
    impact_data = df[impact_cols].apply(pd.value_counts).fillna(0)
    sns.heatmap(impact_data, annot=True, fmt='g', cmap='YlOrRd')
    plt.title('Impact Distribution Heatmap')
    plt.tight_layout()
    plt.savefig('/e:/ML/Analysis/impact_heatmap.png')
    plt.close()
    
    # Impact by District
    plt.figure(figsize=(15, 6))
    district_impact = df.groupby('district')[impact_cols].apply(
        lambda x: (x == 'High').mean()
    ).sort_values('economicImpact', ascending=False)
    district_impact.head(10).plot(kind='bar')
    plt.title('High Impact Distribution by Top 10 Districts')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('/e:/ML/Analysis/district_impact.png')
    plt.close()

if __name__ == "__main__":
    df = pd.read_csv('/e:/ML/DataAnalysis/combined_data.csv')
    create_impact_visualizations(df)
