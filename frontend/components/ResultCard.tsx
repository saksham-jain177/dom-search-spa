import { useState } from 'react'
import styles from '@/styles/Home.module.css'

interface ResultCardProps {
    result: {
        score: number
        percentage: number
        dom_path: string
        chunk_text: string
        chunk_html: string
    }
    rank: number
}

export default function ResultCard({ result, rank }: ResultCardProps) {
    const [isExpanded, setIsExpanded] = useState(false)

    return (
        <div className={styles.resultCard}>
            <div className={styles.cardHeader}>
                <div className={styles.rankBadge}>#{rank}</div>
                <div
                    className={`${styles.matchPercentage} ${styles.tooltip}`}
                    data-tooltip="Semantic similarity score converted to percentage"
                >
                    {result.percentage}% Match
                </div>
            </div>

            <div className={styles.domPath}>
                <span className={styles.domPathLabel}>DOM Path:</span>
                <code
                    className={`${styles.domPathValue} ${styles.tooltip}`}
                    data-tooltip="Location of this content in the HTML structure"
                >
                    {result.dom_path}
                </code>
            </div>

            <div className={styles.contentPreview}>
                <p>{result.chunk_text}</p>
            </div>

            <div className={styles.htmlSection}>
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className={styles.expandButton}
                >
                    {isExpanded ? '▼ Hide' : '▶ Show'} Raw HTML
                </button>

                {isExpanded && (
                    <div className={styles.htmlContent}>
                        <pre>
                            <code>{result.chunk_html}</code>
                        </pre>
                    </div>
                )}
            </div>

            <div className={styles.scoreInfo}>
                <span className={styles.scoreLabel}>Relevance Score:</span>
                <span
                    className={`${styles.scoreValue} ${styles.tooltip}`}
                    data-tooltip="Raw cosine similarity score (0.0 to 1.0)"
                >
                    {result.score.toFixed(4)}
                </span>
            </div>
        </div>
    )
}
