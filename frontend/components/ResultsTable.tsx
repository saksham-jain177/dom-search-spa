import { useState } from 'react'
import styles from '@/styles/Home.module.css'

interface SearchResult {
    score: number
    percentage: number
    dom_path: string
    chunk_text: string
    chunk_html: string
}

interface ResultsTableProps {
    results: SearchResult[]
    showBorders: boolean
}

export default function ResultsTable({ results, showBorders }: ResultsTableProps) {
    const [expandedRow, setExpandedRow] = useState<number | null>(null)

    const toggleRow = (index: number) => {
        if (expandedRow === index) {
            setExpandedRow(null)
        } else {
            setExpandedRow(index)
        }
    }

    return (
        <div className={styles.tableContainer}>
            <table className={`${styles.resultsTable} ${showBorders ? styles.resultsTableBordered : ''}`}>
                <thead>
                    <tr>
                        <th style={{ width: '60px' }}>Rank</th>
                        <th style={{ width: '100px' }}>Match</th>
                        <th>Content Preview</th>
                        <th style={{ width: '100px' }}>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {results.map((result, index) => (
                        <>
                            <tr
                                key={index}
                                className={expandedRow === index ? styles.expandedRow : ''}
                                onClick={() => toggleRow(index)}
                            >
                                <td className={styles.rankCell}>#{index + 1}</td>
                                <td>
                                    <span className={styles.tableMatchBadge}>
                                        {result.percentage}%
                                    </span>
                                </td>
                                <td className={styles.contentCell}>
                                    <div className={styles.tableContentPreview}>
                                        {result.chunk_text}
                                    </div>
                                    <div className={styles.tableDomPath}>
                                        {result.dom_path}
                                    </div>
                                </td>
                                <td>
                                    <button className={styles.tableActionButton}>
                                        {expandedRow === index ? 'Close' : 'View'}
                                    </button>
                                </td>
                            </tr>
                            {expandedRow === index && (
                                <tr className={styles.detailsRow}>
                                    <td colSpan={4}>
                                        <div className={styles.detailsContent}>
                                            <div className={styles.detailsSection}>
                                                <h4>Full Content</h4>
                                                <p>{result.chunk_text}</p>
                                            </div>
                                            <div className={styles.detailsSection}>
                                                <h4>DOM Path</h4>
                                                <code className={styles.domPathValue}>{result.dom_path}</code>
                                            </div>
                                            <div className={styles.detailsSection}>
                                                <h4>Raw HTML</h4>
                                                <pre><code>{result.chunk_html}</code></pre>
                                            </div>
                                            <div className={styles.detailsMeta}>
                                                Relevance Score: <strong>{result.score.toFixed(4)}</strong>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            )}
                        </>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
