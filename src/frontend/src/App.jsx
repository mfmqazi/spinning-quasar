import { useState, useEffect } from 'react'
import axios from 'axios'
import ReactPlayer from 'react-player'
import { Search, Sparkles, MessageSquare, Calendar, BookOpen, ChevronDown, ChevronUp, Image as ImageIcon, Layers } from 'lucide-react'

// Production detection and URL helper
const IS_PROD = import.meta.env.PROD;

const resolveAssetUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  if (IS_PROD) {
    // In prod, assets are served relative to the base URL
    // import.meta.env.BASE_URL usually ends with a slash
    const base = import.meta.env.BASE_URL;
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    return `${base}${cleanPath}`;
  }
  // In dev, assuming the backend specific port if not proxied
  return `http://localhost:8001${path}`;
};

function App() {
  const [timeline, setTimeline] = useState([])
  const [filteredTimeline, setFilteredTimeline] = useState([])
  const [search, setSearch] = useState('')
  const [selectedDate, setSelectedDate] = useState(null)
  const [summary, setSummary] = useState('')
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [expandedTranscripts, setExpandedTranscripts] = useState({})

  // Helper to highlight text matching the search query
  const highlightText = (text) => {
    if (!search || !text) return text;
    // Split text by the search term (case insensitive)
    // We use capture group in regex so the delimiter (the search term) is included in results
    const parts = text.split(new RegExp(`(${search})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === search.toLowerCase() ? (
        <span key={i} className="bg-yellow-300 text-black px-0.5 rounded shadow-sm font-semibold">{part}</span>
      ) : (
        part
      )
    );
  };

  useEffect(() => {
    fetchTimeline()
  }, [])

  useEffect(() => {
    // 1. Filter by Search
    let result = timeline
    if (search) {
      const lower = search.toLowerCase()
      result = result.map(day => {
        const matchingMsgs = day.messages.filter(m =>
          m.content.toLowerCase().includes(lower) ||
          m.sender.toLowerCase().includes(lower)
        )
        if (matchingMsgs.length > 0) {
          return { ...day, messages: matchingMsgs }
        }
        return null
      }).filter(Boolean)
    }

    // 2. Filter by Date (if selected)
    if (selectedDate) {
      result = result.filter(day => day.date === selectedDate)
    }

    setFilteredTimeline(result)
  }, [search, timeline, selectedDate])

  const fetchTimeline = async () => {
    try {
      // In prod, use static JSON. in Dev, use API.
      const url = IS_PROD
        ? `${import.meta.env.BASE_URL}timeline.json`
        : 'http://localhost:8001/api/timeline';

      const res = await axios.get(url)
      setTimeline(res.data)
      setFilteredTimeline(res.data)
    } catch (err) {
      console.error("Failed to fetch timeline", err)
      // Fallback in dev to look for local file if backend is down
      if (!IS_PROD) {
        try {
          const res = await axios.get('/timeline.json');
          setTimeline(res.data);
          setFilteredTimeline(res.data);
        } catch (e) {/* ignore */ }
      }
    }
  }

  const handleSummarize = async (text) => {
    setLoadingSummary(true)
    setSummary('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
    try {
      const res = await axios.post(`${API_BASE}/summary`, { text })
      setSummary(res.data.summary)
    } catch (err) {
      console.error(err)
      alert("Failed to generate summary")
    } finally {
      setLoadingSummary(false)
    }
  }

  const toggleTranscript = (idx) => {
    setExpandedTranscripts(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }))
  }

  // Fallback URL extractor if backend didn't provide one
  const extractUrl = (text) => {
    if (!text) return null
    const urlLineMatch = text.match(/URL:\s*(https?:\/\/[^\s]+)/)
    if (urlLineMatch) return urlLineMatch[1]

    const match = text.match(/(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/[^\s]+)/)
    return match ? match[0] : null
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 pb-32 transition-colors duration-500">

      {/* Jazzy Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-white/80 border-b border-indigo-100 shadow-sm transition-all duration-300">
        <div className="max-w-5xl mx-auto px-4 py-4 flex flex-col md:flex-row items-center justify-between gap-4">

          <div className="flex items-center gap-3 group cursor-pointer" onClick={() => { setSelectedDate(null); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
            <div className="p-2.5 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg group-hover:shadow-indigo-500/30 transition-all duration-300 group-hover:scale-105">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 tracking-tight">
              LMKHealth<span className="font-light text-slate-500">Archive</span>
            </h1>
          </div>

          <div className="relative w-full md:w-96 group">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-indigo-400 group-focus-within:text-indigo-600 transition-colors" />
            </div>
            <input
              type="text"
              placeholder="Search conversations..."
              className="block w-full pl-11 pr-4 py-2.5 bg-indigo-50/50 border border-indigo-100 rounded-2xl text-slate-700 placeholder:text-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:bg-white transition-all duration-300 shadow-inner"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">

        {/* Month Filter & Batch Navigation */}
        <div className="flex items-center justify-between mb-6 px-1">
          <h2 className="text-sm font-bold text-indigo-900/60 uppercase tracking-widest flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            October 2025 (Batch 1)
          </h2>
        </div>

        {/* Date Navigation Bar */}
        <div className="mb-10 overflow-x-auto pb-4 scrollbar-hide">
          <div className="flex gap-3 min-w-max px-1">
            <button
              onClick={() => setSelectedDate(null)}
              className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 shadow-md ${!selectedDate
                ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-indigo-500/30 scale-105'
                : 'bg-white text-slate-600 hover:bg-indigo-50 hover:text-indigo-600'
                }`}
            >
              All Dates
            </button>
            {timeline.map((day, idx) => {
              // Simplified label logic if needed, but strict date works well
              let label = day.date;
              return (
                <button
                  key={day.date}
                  onClick={() => setSelectedDate(day.date === selectedDate ? null : day.date)}
                  className={`px-5 py-2.5 rounded-full text-sm font-medium transition-all duration-300 shadow-sm border ${day.date === selectedDate
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white border-transparent shadow-indigo-500/30 scale-105'
                    : 'bg-white text-slate-600 border-indigo-100 hover:border-indigo-300 hover:text-indigo-700'
                    }`}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>

        {summary && (
          <div className="mb-8 p-6 bg-indigo-50 rounded-3xl border border-indigo-100 shadow-lg animate-fade-in relative">
            <button onClick={() => setSummary('')} className="absolute top-4 right-4 text-indigo-400 hover:text-indigo-700 transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-indigo-100">✕</button>
            <div className="flex items-center gap-2 mb-3 text-indigo-800 font-bold text-lg">
              <Sparkles className="w-5 h-5 text-indigo-500" />
              <h3>AI Summary</h3>
            </div>
            <p className="text-indigo-900 leading-relaxed font-medium">{summary}</p>
          </div>
        )}

        {loadingSummary && (
          <div className="fixed inset-0 bg-white/60 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="bg-white p-6 rounded-2xl shadow-2xl flex items-center gap-4 border border-indigo-50">
              <div className="animate-spin rounded-full h-6 w-6 border-3 border-indigo-500 border-t-transparent"></div>
              <span className="text-base font-semibold text-slate-700">Generating summary...</span>
            </div>
          </div>
        )}

        {/* Timeline Content */}
        <div className="space-y-16">
          {filteredTimeline.map((day, dayIndex) => (
            <div key={day.date} className="relative">

              {/* Date Separator */}
              <div className="sticky top-24 z-10 flex justify-center mb-10">
                <div className="px-6 py-2 bg-white/95 backdrop-blur-md rounded-full shadow-lg border border-indigo-100 ring-1 ring-indigo-50/50 flex items-center gap-2 transform hover:scale-105 transition-transform duration-300">
                  <Calendar className="w-4 h-4 text-indigo-500" />
                  <span className="text-sm font-bold text-indigo-700 tracking-wide">
                    {day.date}
                  </span>
                </div>
              </div>

              <div className="space-y-8">
                {day.messages.map((msg, msgIndex) => {
                  const isImage = msg.type === 'image'
                  const isTranscript = msg.type === 'transcript' || (msg.content && typeof msg.content === 'string' && msg.content.includes("[Video Transcript]"));
                  const uniqueId = `${day.date}-${msgIndex}`
                  const expanded = expandedTranscripts[uniqueId]
                  const showPlayer = Boolean(msg.video_url)

                  return (
                    <div
                      key={msgIndex}
                      className={`group relative p-6 sm:p-8 rounded-[2rem] transition-all duration-300 hover:shadow-2xl hover:-translate-y-1 border ${isTranscript
                        ? 'bg-gradient-to-br from-amber-50 via-orange-50/30 to-white border-orange-100/60'
                        : 'bg-white border-indigo-50/60 shadow-xl shadow-indigo-100/10'
                        }`}
                    >
                      {/* Sender Avatar & Name */}
                      <div className="flex items-start gap-5 mb-4">
                        <div className={`mt-1 w-12 h-12 rounded-2xl flex items-center justify-center text-lg font-bold shadow-lg transform group-hover:rotate-6 transition-transform duration-300 ${isTranscript ? 'bg-gradient-to-br from-orange-100 to-amber-100 text-orange-600' : 'bg-gradient-to-br from-indigo-100 to-purple-100 text-indigo-600'
                          }`}>
                          {msg.sender.charAt(0).toUpperCase()}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-baseline mb-2">
                            <h3 className={`font-bold text-lg truncate ${isTranscript ? 'text-orange-900' : 'text-slate-800'
                              }`}>
                              {isTranscript ? "Video Transcript" : highlightText(msg.sender)}
                            </h3>
                            <span className="text-xs font-semibold text-slate-400 bg-slate-50 px-2.5 py-1 rounded-full border border-slate-100 w-fit mt-1 sm:mt-0">
                              {msg.time}
                            </span>
                          </div>

                          {/* Message Content */}
                          <div className={`text-[17px] leading-relaxed break-words font-medium ${isTranscript ? 'text-slate-600 italic' : 'text-slate-600'
                            }`}>
                            {isTranscript ? (
                              <div>
                                <div className={`relative ${!expanded ? 'line-clamp-4' : ''}`}>
                                  {highlightText(msg.content)}
                                  {!expanded && (
                                    <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-amber-50 to-transparent pointer-events-none" />
                                  )}
                                </div>
                              </div>
                            ) : (
                              msg.type === 'text' ? (
                                <>
                                  {highlightText(msg.content)}
                                </>
                              ) : null
                            )}
                          </div>

                          {/* Video Player Box */}
                          {showPlayer && (() => {
                            const videoIdMatch = msg.video_url.match(/(?:v=|youtu\.be\/|embed\/)([\w\-]+)/);
                            const videoId = videoIdMatch ? videoIdMatch[1] : null;
                            const thumbnailUrl = videoId
                              ? `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`
                              : null;

                            return (
                              <div className="mt-6 bg-slate-900 rounded-2xl overflow-hidden shadow-2xl w-full max-w-[560px] mx-auto ring-4 ring-slate-50 relative group/player">
                                <a
                                  href={msg.video_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="block relative aspect-video bg-black overflow-hidden"
                                >
                                  {thumbnailUrl ? (
                                    <img
                                      src={thumbnailUrl}
                                      alt="Video thumbnail"
                                      className="w-full h-full object-cover opacity-90 group-hover/player:opacity-100 transition-all duration-700 transform group-hover/player:scale-105"
                                    />
                                  ) : (
                                    <div className="w-full h-full flex items-center justify-center text-white text-opacity-50">
                                      No Thumbnail
                                    </div>
                                  )}
                                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                    <div className="w-16 h-16 bg-red-600/90 backdrop-blur-md rounded-full flex items-center justify-center shadow-xl group-hover/player:scale-110 transition-transform duration-300 ring-4 ring-white/20">
                                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" className="w-8 h-8 ml-1">
                                        <path d="M8 5v14l11-7z" />
                                      </svg>
                                    </div>
                                  </div>
                                </a>
                                <div className="px-4 py-3 bg-slate-800 border-t border-slate-700/50 flex items-center justify-between">
                                  <div className="flex items-center gap-2 text-white">
                                    <span className="flex h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>
                                    <span className="text-xs font-bold tracking-wide uppercase text-slate-400">YouTube</span>
                                  </div>
                                  <a href={msg.video_url} target="_blank" rel="noreferrer" className="text-xs font-medium text-blue-400 hover:text-blue-300 hover:underline flex items-center gap-1">
                                    Open <span className="hidden sm:inline">in new tab</span> &rarr;
                                  </a>
                                </div>
                              </div>
                            );
                          })()}

                          {/* Image Display */}
                          {isImage && (
                            <div className="mt-5 rounded-2xl overflow-hidden shadow-xl border-4 border-white transform transition-transform duration-500 hover:scale-[1.01]">
                              <img
                                src={resolveAssetUrl(msg.content)}
                                alt="Gallery Item"
                                className="w-full h-auto max-h-[600px] object-cover"
                                loading="lazy"
                              />
                            </div>
                          )}

                        </div>
                      </div>

                      {/* Footer Actions */}
                      <div className="pl-[4.25rem] flex items-center justify-end mt-4 pt-3 border-t border-dashed border-indigo-100/50 gap-3">
                        {isTranscript && (
                          <button
                            onClick={() => toggleTranscript(uniqueId)}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-orange-600 bg-orange-50 hover:bg-orange-100 hover:text-orange-700 transition-all duration-300 group/btn"
                          >
                            {expanded ? (
                              <><ChevronUp className="w-3 h-3 group-hover/btn:-translate-y-0.5 transition-transform" /> Show Less</>
                            ) : (
                              <><ChevronDown className="w-3 h-3 group-hover/btn:translate-y-0.5 transition-transform" /> Read Transcript</>
                            )}
                          </button>
                        )}
                        {/* Show summarize for transcripts OR long text messages (>300 chars) */}
                        {(isTranscript || (msg.type === 'text' && msg.content.length > 300)) && (
                          <button
                            onClick={() => handleSummarize(msg.content)}
                            className="text-xs font-medium text-indigo-400 hover:text-indigo-600 transition-colors flex items-center gap-1.5 p-2 rounded-lg hover:bg-indigo-50"
                            title="Summarize using AI"
                          >
                            <Sparkles className="w-3.5 h-3.5" />
                            <span className="hidden sm:inline">Summarize</span>
                          </button>
                        )}
                      </div>

                    </div>
                  )
                })}
              </div>
            </div>
          ))}

          {filteredTimeline.length === 0 && (
            <div className="text-center py-32 bg-white rounded-3xl shadow-xl border border-indigo-50 mx-4">
              <div className="inline-block p-6 rounded-3xl bg-indigo-50 mb-6">
                <Search className="w-12 h-12 text-indigo-300" />
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">No matching conversations</h3>
              <p className="text-slate-500">Try searching for a different keyword or date.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
