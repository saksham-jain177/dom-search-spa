import { useState, FormEvent, useRef, useEffect } from 'react'
import styles from '@/styles/Home.module.css'

interface SearchBarProps {
    onResults: (results: SearchResult[], totalChunks: number, query: string) => void
    onError: (error: string) => void
}

interface SearchResult {
    score: number
    percentage: number
    dom_path: string
    chunk_text: string
    chunk_html: string
}

export default function SearchBar({ onResults, onError }: SearchBarProps) {
    const [url, setUrl] = useState('')
    const [query, setQuery] = useState('')
    const [loading, setLoading] = useState(false)
    const [progress, setProgress] = useState('')

    const urlInputRef = useRef<HTMLInputElement>(null)
    const queryInputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Ignore if user is already typing in an input
            if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
                return
            }

            if (e.key === '/') {
                e.preventDefault()
                urlInputRef.current?.focus()
            } else if (e.key === '\\') {
                e.preventDefault()
                queryInputRef.current?.focus()
            }
        }

        window.addEventListener('keydown', handleKeyDown)
        return () => window.removeEventListener('keydown', handleKeyDown)
    }, [])

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault()

        // Validation
        if (!url.trim()) {
            onError('Please enter a website URL')
            return
        }
        if (!query.trim()) {
            onError('Please enter a search query')
            return
        }

        setLoading(true)
        setProgress('Fetching HTML...')
        onError('') // Clear previous errors

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            const response = await fetch(`${apiUrl}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, query }),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Search failed')
            }

            const data = await response.json()
            onResults(data.results, data.total_chunks, data.query)
            setProgress('')
        } catch (error) {
            onError(error instanceof Error ? error.message : 'An error occurred')
            setProgress('')
        } finally {
            setLoading(false)
        }
    }

    return (
        <>
            <form onSubmit={handleSubmit} className={styles.searchForm}>
                <div className={styles.inputGroup}>
                    <label htmlFor="url" className={styles.label}>
                        Website URL{' '}
                        <span
                            className={styles.tooltip}
                            data-tooltip="Enter the full URL of the page you want to search (e.g., https://example.com)"
                        >
                            ⓘ
                        </span>
                    </label>
                    <input
                        id="url"
                        ref={urlInputRef}
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com (Press '/')"
                        className={styles.input}
                        disabled={loading}
                    />
                </div>

                <div className={styles.inputGroup}>
                    <label htmlFor="query" className={styles.label}>
                        Search Query{' '}
                        <span
                            className={styles.tooltip}
                            data-tooltip="Enter keywords or a natural language question to find relevant content"
                        >
                            ⓘ
                        </span>
                    </label>
                    <input
                        id="query"
                        ref={queryInputRef}
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter your search query... (Press '\')"
                        className={styles.input}
                        disabled={loading}
                    />
                </div>

                <button
                    type="submit"
                    className={styles.submitButton}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <span className={styles.spinner}></span>
                            Searching...
                        </>
                    ) : (
                        'Search'
                    )}
                </button>
            </form>

            {/* Loading Modal */}
            {loading && (
                <div className={styles.modalOverlay}>
                    <div className={styles.modalContent}>
                        <div className={styles.modalSpinner}></div>
                        <h3>Processing Your Search</h3>
                        <p className={styles.progressText}>{progress || 'Please wait...'}</p>
                        <div className={styles.progressSteps}>
                            <div className={styles.step}>1. Fetching HTML</div>
                            <div className={styles.step}>2. Parsing content</div>
                            <div className={styles.step}>3. Creating embeddings</div>
                            <div className={styles.step}>4. Searching database</div>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
