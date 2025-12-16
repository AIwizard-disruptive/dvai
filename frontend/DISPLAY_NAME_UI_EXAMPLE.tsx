/**
 * UI Examples for Displaying Cleaned Document Names
 * 
 * Shows how to use display_name instead of filename for better UX
 */

// ============================================================================
// Example 1: Meeting Card Component
// ============================================================================

interface Meeting {
  id: string;
  filename: string;
  display_name?: string;  // May be null for old documents
  meeting_date: string;
  duration_minutes?: number;
}

export function MeetingCard({ meeting }: { meeting: Meeting }) {
  return (
    <div className="meeting-card border rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Use display_name if available, fallback to filename */}
      <h3 className="text-lg font-semibold">
        {meeting.display_name || meeting.filename}
      </h3>
      
      {/* Show original filename on hover for reference */}
      <p className="text-sm text-gray-500 truncate" title={meeting.filename}>
        {meeting.meeting_date} 
        {meeting.duration_minutes && ` • ${meeting.duration_minutes} min`}
      </p>
      
      {/* Optional: Show that it's a cleaned name */}
      {meeting.display_name && (
        <span className="text-xs text-green-600">✓ Clean name</span>
      )}
    </div>
  );
}

// ============================================================================
// Example 2: Document List with Before/After Toggle
// ============================================================================

import { useState } from 'react';

interface Document {
  id: string;
  filename: string;
  display_name?: string;
  file_size: number;
  uploaded_at: string;
}

export function DocumentList({ documents }: { documents: Document[] }) {
  const [showOriginal, setShowOriginal] = useState(false);
  
  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Documents</h2>
        
        {/* Toggle to show original filenames */}
        <button
          onClick={() => setShowOriginal(!showOriginal)}
          className="text-sm text-gray-600 hover:text-gray-900"
        >
          {showOriginal ? 'Show clean names' : 'Show original names'}
        </button>
      </div>
      
      <div className="space-y-2">
        {documents.map(doc => (
          <div key={doc.id} className="flex items-center gap-3 p-3 border rounded hover:bg-gray-50">
            <div className="flex-1">
              <p className="font-medium">
                {showOriginal ? doc.filename : (doc.display_name || doc.filename)}
              </p>
              <p className="text-sm text-gray-500">
                {new Date(doc.uploaded_at).toLocaleDateString()} • {formatFileSize(doc.file_size)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Example 3: Meeting View Selector (Your Screenshot)
// ============================================================================

interface MeetingView {
  id: string;
  filename: string;
  display_name?: string;
  meeting_date: string;
  duration_minutes?: number;
  priority?: string;
}

export function MeetingsView({ meetings }: { meetings: MeetingView[] }) {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Meetings ({meetings.length})</h1>
        <div className="flex gap-2">
          <button className="p-2 hover:bg-gray-100 rounded">
            <GridIcon />
          </button>
          <button className="p-2 hover:bg-gray-100 rounded">
            <ListIcon />
          </button>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {meetings.map(meeting => (
          <div 
            key={meeting.id} 
            className="border rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
          >
            {/* Cleaned name as the main title */}
            <h3 className="font-semibold text-lg mb-2 line-clamp-2">
              {meeting.display_name || meeting.filename}
            </h3>
            
            <div className="space-y-1 text-sm text-gray-600">
              {meeting.meeting_date && (
                <p>{new Date(meeting.meeting_date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric'
                })}</p>
              )}
              
              {meeting.duration_minutes && (
                <p>{meeting.duration_minutes} min • {meeting.priority || 'None'}</p>
              )}
            </div>
            
            {/* Show original filename as tooltip */}
            {meeting.display_name && meeting.display_name !== meeting.filename && (
              <p className="text-xs text-gray-400 mt-2 truncate" title={meeting.filename}>
                Original: {meeting.filename}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Example 4: Search with Cleaned Names
// ============================================================================

export function DocumentSearch({ documents }: { documents: Document[] }) {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Search both display_name and original filename
  const filteredDocs = documents.filter(doc => {
    const search = searchTerm.toLowerCase();
    const displayName = (doc.display_name || doc.filename).toLowerCase();
    const originalName = doc.filename.toLowerCase();
    
    return displayName.includes(search) || originalName.includes(search);
  });
  
  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search documents..."
        className="w-full p-2 border rounded mb-4"
      />
      
      <div className="space-y-2">
        {filteredDocs.map(doc => (
          <div key={doc.id} className="p-3 border rounded">
            {/* Highlight matches in display name */}
            <p className="font-medium">
              <HighlightText 
                text={doc.display_name || doc.filename} 
                highlight={searchTerm}
              />
            </p>
            
            {/* Also show if match was in original filename */}
            {doc.display_name && doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) && (
              <p className="text-xs text-gray-500">
                Found in original: <HighlightText text={doc.filename} highlight={searchTerm} />
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Example 5: API Query (Fetch documents with display_name)
// ============================================================================

/**
 * Fetch documents from API
 */
export async function fetchDocuments(orgId: string): Promise<Document[]> {
  const response = await fetch(`/api/documents?org_id=${orgId}`, {
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
    },
  });
  
  const data = await response.json();
  return data;
}

/**
 * SQL query example for backend
 */
const GET_DOCUMENTS_QUERY = `
  SELECT 
    id,
    filename,
    display_name,  -- Always include this!
    file_size,
    mime_type,
    uploaded_at,
    uploaded_by
  FROM uploaded_documents
  WHERE org_id = $1
  ORDER BY uploaded_at DESC
`;

// ============================================================================
// Helper Functions
// ============================================================================

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function HighlightText({ text, highlight }: { text: string; highlight: string }) {
  if (!highlight.trim()) return <span>{text}</span>;
  
  const regex = new RegExp(`(${highlight})`, 'gi');
  const parts = text.split(regex);
  
  return (
    <span>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="bg-yellow-200">{part}</mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
}

function GridIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
  );
}

function ListIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
    </svg>
  );
}

// ============================================================================
// Usage Summary
// ============================================================================

/**
 * KEY POINTS:
 * 
 * 1. Always use: meeting.display_name || meeting.filename
 *    - This ensures fallback for old documents
 * 
 * 2. Consider showing original filename as tooltip or on hover
 *    - Helpful for debugging/reference
 * 
 * 3. Search both display_name and filename
 *    - Users might search by original name
 * 
 * 4. In API queries, always SELECT display_name
 *    - Don't forget to include it in your queries!
 * 
 * 5. Visual indicator for cleaned names (optional)
 *    - Small checkmark or badge showing "clean name"
 */

