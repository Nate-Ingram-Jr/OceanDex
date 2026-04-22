import { useState, useRef } from 'react'

export default function IDScanner() {
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const fileRef = useRef()

  function handleFile(e) {
    const [loading, setloading] = useState(false)
    const [error, setError] = useState(null)

    async function handleFile(e) {
      const file = e.target.files[0]
      if (!file) return

      setPreview(URL.createObjectURL(file))
      setResult(null)
      setError(null)
      setLoading(true)

      const formData = new FormData()
      formData.append('image', file)

      try {
        const res = await fetch('/api/scan', {method: 'POST', body: formData}
          if (!res.ok) throw new Error('Scan failed')
            const data = await res.json()
            setResult(data)
      } catch {
          setError('Failed to identify the creature. Please try again with a clearer photo.')
      } finally {
          setLoading(false)
      }

}
        )
    }
    })
  }

  return (
    <div className="scanner-page">
      <div className="scanner-intro">
        <h2>ID Scanner</h2>
        <p>Point your camera at any sea creature to identify it instantly.</p>
        <p>Works with fish, sharks, rays, shellfish, and more.</p>
      </div>

      <div className="scanner-viewport">
        {preview ? (
          <img src={preview} alt="Uploaded" className="scanner-preview" />
        ) : (
          <div className="scanner-frame">
            <div className="scanner-corner tl" />
            <div className="scanner-corner tr" />
            <div className="scanner-corner bl" />
            <div className="scanner-corner br" />
            <span className="scanner-placeholder">[ Live Camera Feed ]</span>
          </div>
        )}
        <button className="capture-btn" onClick={() => fileRef.current.click()}>
          {preview ? '↺ Scan Another' : 'Tap to capture'}
        </button>
      </div>

      <div className="scanner-upload">
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleFile}
        />
        <button className="upload-btn" onClick={() => fileRef.current.click()}>
          OR upload a photo from your library
        </button>
      </div>

      {result && (
        <div className="scanner-result">
          <p className="result-label">IDENTIFICATION RESULT</p>
          <div className="result-card">
            <div className="result-img-placeholder">Detected</div>
            <div className="result-info">
              <h3>{result.name}</h3>
              <p className="result-sci">{result.scientific}</p>
              <span className="result-confidence">{result.confidence}% confidence</span>
              <span className="result-iucn">■ {result.iucn}</span>
              <button className="result-link">Tap to view full profile →</button>
            </div>
          </div>
        </div>
      )}

      <div className="scanner-tips">
        <p className="result-label">IDENTIFICATION TIPS</p>
        <ul>
          <li>Ensure good lighting and a clear, unobstructed view</li>
          <li>Works best with photos taken within 3 meters of the subject</li>
          <li>For small creatures, use macro mode on your camera</li>
          <li>Multiple angles improve identification accuracy</li>
        </ul>
      </div>
    </div>
  )
}
