import styles from '@/styles/Home.module.css'

interface SearchResult {
    score: number
    percentage: number
}

interface ScoreDistributionProps {
    results: SearchResult[]
}

export default function ScoreDistribution({ results }: ScoreDistributionProps) {
    // Take top 10 results (or fewer)
    const data = results.slice(0, 10)

    return (
        <div className={styles.chartContainer}>
            <h3 className={styles.chartTitle}>Relevance Score Distribution</h3>
            <div className={styles.barChart}>
                {data.map((result, index) => (
                    <div key={index} className={styles.barWrapper}>
                        <div
                            className={styles.bar}
                            style={{ height: `${result.percentage}%` }}
                            title={`Rank #${index + 1}: ${result.percentage}%`}
                        >
                            <span className={styles.barLabel}>{result.percentage}%</span>
                        </div>
                        <span className={styles.barAxisLabel}>#{index + 1}</span>
                    </div>
                ))}
            </div>
            <div className={styles.chartLegend}>
                <span>X-Axis: Result Rank</span>
                <span>Y-Axis: Relevance Score (0-100%)</span>
            </div>
        </div>
    )
}
