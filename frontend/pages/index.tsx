import Head from 'next/head'
import { useState, useEffect } from 'react'
import SearchBar from '@/components/SearchBar'
import ResultCard from '@/components/ResultCard'
import styles from '@/styles/Home.module.css'

interface SearchResult {
    score: number
    percentage: number
    dom_path: string
    chunk_text: string
    chunk_html: string
}

import ResultsTable from '@/components/ResultsTable'

export default function Home() {
    const [results, setResults] = useState<SearchResult[]>([])
    const [totalChunks, setTotalChunks] = useState(0)
    const [query, setQuery] = useState('')
    const [error, setError] = useState('')
    const [theme, setTheme] = useState('dark')
    const [apiHealth, setApiHealth] = useState<'healthy' | 'unhealthy'>('healthy')
    const [viewMode, setViewMode] = useState<'card' | 'table'>('card')

    useEffect(() => {
        const savedTheme = localStorage.getItem('theme')
        if (savedTheme) {
            setTheme(savedTheme)
            document.documentElement.setAttribute('data-theme', savedTheme)
        } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
            setTheme('light')
            document.documentElement.setAttribute('data-theme', 'light')
        }

        checkApiHealth()
        const interval = setInterval(checkApiHealth, 30000)
        return () => clearInterval(interval)
    }, [])

    const checkApiHealth = async () => {
        try {
            const res = await fetch('http://localhost:8000/', { method: 'GET' })
            setApiHealth(res.ok ? 'healthy' : 'unhealthy')
        } catch {
            setApiHealth('unhealthy')
        }
    }

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark'
        setTheme(newTheme)
        document.documentElement.setAttribute('data-theme', newTheme)
        localStorage.setItem('theme', newTheme)
    }

    const handleResults = (newResults: SearchResult[], total: number, q: string) => {
        setResults(newResults)
        setTotalChunks(total)
        setQuery(q)
        setError('')
    }

    return (
        <div className={styles.container}>
            <Head>
                <title>Website Content Search</title>
                <meta name="description" content="Search through website content with precision" />
                <link rel="icon" href="/favicon.ico" />
            </Head>

            <svg style={{ display: 'none' }}>
                <defs>
                    <filter id="gooey">
                        <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur" />
                        <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="gooey" />
                        <feBlend in="SourceGraphic" in2="gooey" />
                    </filter>
                </defs>
            </svg>

            <main className={styles.main}>
                <div className={styles.header}>
                    <div className={styles.themeToggle}>
                        <label className={styles.switch}>
                            <input
                                type="checkbox"
                                checked={theme === 'dark'}
                                onChange={toggleTheme}
                                aria-label="Toggle theme"
                            />
                            <span className={styles.slider}></span>
                        </label>
                    </div>

                    <h1 className={styles.title}>Website Content Search</h1>
                    <p className={styles.subtitle}>
                        Search through website content with precision
                    </p>
                </div>

                <div className={styles.searchSection}>
                    <SearchBar onResults={handleResults} onError={setError} />
                </div>

                {error && (
                    <div className={styles.error}>
                        <span>⚠️</span> {error}
                    </div>
                )}

                {results.length > 0 && (
                    <div className={styles.resultsSection}>
                        <div className={styles.resultsHeader}>
                            <div>
                                <h2>Top Matches</h2>
                                <div className={styles.resultsMeta}>
                                    Found {results.length} matches from <strong>{totalChunks}</strong> chunks
                                </div>
                            </div>

                            <div className={styles.viewToggle}>
                                <button
                                    className={`${styles.toggleButton} ${viewMode === 'card' ? styles.toggleButtonActive : ''}`}
                                    onClick={() => setViewMode('card')}
                                >
                                    Cards
                                </button>
                                <button
                                    className={`${styles.toggleButton} ${viewMode === 'table' ? styles.toggleButtonActive : ''}`}
                                    onClick={() => setViewMode('table')}
                                >
                                    Table
                                </button>
                            </div>
                        </div>

                        {viewMode === 'card' ? (
                            <div className={styles.resultsGrid}>
                                {results.map((result, index) => (
                                    <ResultCard
                                        key={index}
                                        result={result}
                                        rank={index + 1}
                                    />
                                ))}
                            </div>
                        ) : (
                            <ResultsTable results={results} />
                        )}
                    </div>
                )}

                {!error && results.length === 0 && query && (
                    <div className={styles.noResults}>
                        <p>No results found. Try a different query.</p>
                    </div>
                )}
            </main>

            <div
                className={styles.healthIndicator}
                title="API connection status (auto-refreshes every 30s)"
            >
                <div className={`${styles.healthDot} ${apiHealth === 'healthy' ? styles.healthDotHealthy : styles.healthDotUnhealthy}`}></div>
                <span>API: {apiHealth === 'healthy' ? 'Online' : 'Offline'}</span>
            </div>

            <footer className={styles.footer}>
                <p>Powered by FastAPI + Pinecone + Next.js</p>
            </footer>
        </div>
    )
}
