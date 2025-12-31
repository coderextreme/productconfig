import React, { useState, useEffect } from 'react';
import { Calendar, Users, Mail, Globe, Linkedin, Github, MessageCircle, Video, Plus, Edit2, Trash2, Copy, Send, Save, Upload, X, ExternalLink, Moon, Sun } from 'lucide-react';

// Types
interface Contact {
  id: string;
  name: string;
  email: string;
  timezone: string;
  socials: {
    twitter?: string;
    linkedin?: string;
    github?: string;
    messenger?: string;
    discord?: string;
    zoom?: string;
  };
}

interface Meeting {
  id: string;
  topic: string;
  dateTime: string;
  locationType: 'Physical' | 'URL' | 'Zoom' | 'Discord' | 'Facebook Messenger';
  location: string;
  participantIds: string[];
  shareableLink: string;
}

interface AppState {
  contacts: Contact[];
  meetings: Meeting[];
}

// Main App Component
export default function App() {
  const [state, setState] = useState<AppState>({ contacts: [], meetings: [] });
  const [currentView, setCurrentView] = useState<'contacts' | 'meetings'>('contacts');
  const [darkMode, setDarkMode] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);

  useEffect(() => {
    const saved = localStorage.getItem('contactSchedulerData');
    if (saved) {
      setState(JSON.parse(saved));
    }
    const darkPreference = localStorage.getItem('darkMode') === 'true';
    setDarkMode(darkPreference);
  }, []);

  useEffect(() => {
    localStorage.setItem('contactSchedulerData', JSON.stringify(state));
  }, [state]);

  useEffect(() => {
    localStorage.setItem('darkMode', String(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const saveToFile = () => {
    const dataStr = JSON.stringify(state, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `contacts-meetings-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const restoreFromFile = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = (e: any) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const data = JSON.parse(e.target?.result as string);
            setState(data);
            alert('Data restored successfully!');
          } catch (err) {
            alert('Error parsing file. Please ensure it is a valid JSON file.');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const openModal = (content: React.ReactNode) => {
    setModalContent(content);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalContent(null);
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        <Header
          currentView={currentView}
          setCurrentView={setCurrentView}
          saveToFile={saveToFile}
          restoreFromFile={restoreFromFile}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
        />
        <main className="container mx-auto px-4 py-8 max-w-7xl">
          {currentView === 'contacts' ? (
            <ContactList
              contacts={state.contacts}
              setState={setState}
              openModal={openModal}
              closeModal={closeModal}
            />
          ) : (
            <MeetingList
              meetings={state.meetings}
              contacts={state.contacts}
              setState={setState}
              openModal={openModal}
              closeModal={closeModal}
            />
          )}
        </main>
        {modalOpen && (
          <Modal onClose={closeModal}>
            {modalContent}
          </Modal>
        )}
      </div>
    </div>
  );
}

// Header Component
function Header({ currentView, setCurrentView, saveToFile, restoreFromFile, darkMode, setDarkMode }: any) {
  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-gray-800 shadow-md transition-colors">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between max-w-7xl">
        <div className="flex items-center gap-6">
          <h1 className="text-2xl font-bold text-blue-600 dark:text-blue-400">Contact Scheduler</h1>
          <nav className="flex gap-2">
            <button
              onClick={() => setCurrentView('contacts')}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                currentView === 'contacts'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <Users size={18} />
              <span>Contacts</span>
            </button>
            <button
              onClick={() => setCurrentView('meetings')}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                currentView === 'meetings'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              <Calendar size={18} />
              <span>Meetings</span>
            </button>
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            title={darkMode ? 'Light mode' : 'Dark mode'}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <button
            onClick={saveToFile}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            title="Save to File"
          >
            <Save size={20} />
          </button>
          <button
            onClick={restoreFromFile}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            title="Restore from File"
          >
            <Upload size={20} />
          </button>
          <button
            onClick={() => alert('Server backup feature coming soon!')}
            className="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors"
          >
            Server Backup
          </button>
        </div>
      </div>
    </header>
  );
}

// Modal Component
function Modal({ children, onClose }: any) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50" onClick={onClose}>
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}

// Contact List Component
function ContactList({ contacts, setState, openModal, closeModal }: any) {
  const addContact = () => {
    openModal(
      <ContactForm
        onSave={(contact: Contact) => {
          setState((prev: AppState) => ({
            ...prev,
            contacts: [...prev.contacts, { ...contact, id: crypto.randomUUID() }],
          }));
          closeModal();
        }}
        onCancel={closeModal}
      />
    );
  };

  const editContact = (contact: Contact) => {
    openModal(
      <ContactForm
        contact={contact}
        onSave={(updated: Contact) => {
          setState((prev: AppState) => ({
            ...prev,
            contacts: prev.contacts.map((c) => (c.id === updated.id ? updated : c)),
          }));
          closeModal();
        }}
        onCancel={closeModal}
      />
    );
  };

  const deleteContact = (id: string) => {
    if (confirm('Are you sure you want to delete this contact?')) {
      setState((prev: AppState) => ({
        ...prev,
        contacts: prev.contacts.filter((c) => c.id !== id),
        meetings: prev.meetings.map((m) => ({
          ...m,
          participantIds: m.participantIds.filter((pid) => pid !== id),
        })),
      }));
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100">Contacts</h2>
        <button
          onClick={addContact}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
        >
          <Plus size={20} />
          Add Contact
        </button>
      </div>
      {contacts.length === 0 ? (
        <div className="text-center py-16 text-gray-500 dark:text-gray-400">
          <Users size={64} className="mx-auto mb-4 opacity-50" />
          <p className="text-xl">No contacts yet. Click "Add Contact" to get started!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contacts.map((contact: Contact) => (
            <ContactCard
              key={contact.id}
              contact={contact}
              onEdit={() => editContact(contact)}
              onDelete={() => deleteContact(contact.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Contact Card Component
function ContactCard({ contact, onEdit, onDelete }: any) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-1">{contact.name}</h3>
          <p className="text-gray-600 dark:text-gray-400 text-sm">{contact.email}</p>
          <p className="text-gray-500 dark:text-gray-500 text-sm mt-1 flex items-center gap-1">
            <Globe size={14} />
            {contact.timezone}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={onEdit}
            className="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-700 rounded transition-colors"
            title="Edit"
          >
            <Edit2 size={18} />
          </button>
          <button
            onClick={onDelete}
            className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-gray-700 rounded transition-colors"
            title="Delete"
          >
            <Trash2 size={18} />
          </button>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {contact.socials.twitter && (
          <a
            href={`https://twitter.com/${contact.socials.twitter}`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            title="Twitter"
          >
            <Globe size={16} />
          </a>
        )}
        {contact.socials.linkedin && (
          <a
            href={contact.socials.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            title="LinkedIn"
          >
            <Linkedin size={16} />
          </a>
        )}
        {contact.socials.github && (
          <a
            href={`https://github.com/${contact.socials.github}`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            title="GitHub"
          >
            <Github size={16} />
          </a>
        )}
        {contact.socials.messenger && (
          <a
            href={`https://m.me/${contact.socials.messenger}`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            title="Messenger"
          >
            <MessageCircle size={16} />
          </a>
        )}
        {contact.socials.discord && (
          <span className="p-2 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded text-sm" title="Discord">
            {contact.socials.discord}
          </span>
        )}
        {contact.socials.zoom && (
          <a
            href={contact.socials.zoom.startsWith('http') ? contact.socials.zoom : `https://zoom.us/j/${contact.socials.zoom}`}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            title="Zoom"
          >
            <Video size={16} />
          </a>
        )}
      </div>
    </div>
  );
}

// Contact Form Component
function ContactForm({ contact, onSave, onCancel }: any) {
  const [formData, setFormData] = useState<Contact>(
    contact || {
      id: '',
      name: '',
      email: '',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      socials: {},
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          {contact ? 'Edit Contact' : 'Add Contact'}
        </h2>
        <button type="button" onClick={onCancel} className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
          <X size={24} />
        </button>
      </div>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email *</label>
          <input
            type="email"
            required
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Timezone *</label>
          <input
            type="text"
            required
            value={formData.timezone}
            onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder="e.g., America/New_York"
          />
        </div>
        <div className="border-t dark:border-gray-600 pt-4">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-3">Social Profiles</h3>
          <div className="space-y-3">
            <input
              type="text"
              placeholder="Twitter username"
              value={formData.socials.twitter || ''}
              onChange={(e) => setFormData({ ...formData, socials: { ...formData.socials, twitter: e.target.value } })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
            <input
              type="url"
              placeholder="LinkedIn profile URL"
              value={formData.socials.linkedin || ''}
              onChange={(e) => setFormData({ ...formData, socials: { ...formData.socials, linkedin: e.target.value } })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
            <input
              type="text"
              placeholder="GitHub username"
              value={formData.socials.github || ''}
              onChange={(e) => setFormData({ ...formData, socials: { ...formData.socials, github: e.target.value } })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
            <input
              type="text"
              placeholder="Facebook Messenger username"
              value={formData.socials.messenger || ''}
              onChange={(e) => setFormData({ ...formData, socials: { ...formData.socials, messenger: e.target.value } })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
            <input
              type="text"
              placeholder="Discord username (e.g., user#1234)"
              value={formData.socials.discord || ''}
              onChange={(e) => setFormData({ ...formData, socials: { ...formData.socials, discord: e.target.value } })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
            <input
              type="text"
              placeholder="Zoom meeting ID or link"
              value={formData.socials.zoom || ''}
              onChange={(e) => setFormData({ ...formData, socials: { ...formData.socials, zoom: e.target.value } })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            />
          </div>
        </div>
      </div>
      <div className="flex gap-3 mt-6">
        <button
          type="submit"
          className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {contact ? 'Update' : 'Add'} Contact
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

// Meeting List Component
function MeetingList({ meetings, contacts, setState, openModal, closeModal }: any) {
  const addMeeting = () => {
    openModal(
      <MeetingForm
        contacts={contacts}
        onSave={(meeting: Meeting) => {
          const id = crypto.randomUUID();
          const shareableLink = `${window.location.origin}/join?meetingId=${id}`;
          setState((prev: AppState) => ({
            ...prev,
            meetings: [...prev.meetings, { ...meeting, id, shareableLink }],
          }));
          closeModal();
        }}
        onCancel={closeModal}
      />
    );
  };

  const editMeeting = (meeting: Meeting) => {
    openModal(
      <MeetingForm
        meeting={meeting}
        contacts={contacts}
        onSave={(updated: Meeting) => {
          setState((prev: AppState) => ({
            ...prev,
            meetings: prev.meetings.map((m) => (m.id === updated.id ? updated : m)),
          }));
          closeModal();
        }}
        onCancel={closeModal}
      />
    );
  };

  const deleteMeeting = (id: string) => {
    if (confirm('Are you sure you want to delete this meeting?')) {
      setState((prev: AppState) => ({
        ...prev,
        meetings: prev.meetings.filter((m) => m.id !== id),
      }));
    }
  };

  const composeEmail = (meeting: Meeting) => {
    openModal(
      <EmailComposer meeting={meeting} contacts={contacts} onClose={closeModal} />
    );
  };

  const sortedMeetings = [...meetings].sort((a, b) => 
    new Date(a.dateTime).getTime() - new Date(b.dateTime).getTime()
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800 dark:text-gray-100">Meetings</h2>
        <button
          onClick={addMeeting}
          disabled={contacts.length === 0}
          className={`px-6 py-3 rounded-lg flex items-center gap-2 transition-colors ${
            contacts.length === 0
              ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
          title={contacts.length === 0 ? 'Add contacts first' : ''}
        >
          <Plus size={20} />
          Schedule Meeting
        </button>
      </div>
      {meetings.length === 0 ? (
        <div className="text-center py-16 text-gray-500 dark:text-gray-400">
          <Calendar size={64} className="mx-auto mb-4 opacity-50" />
          <p className="text-xl">
            {contacts.length === 0
              ? 'Add some contacts first, then schedule meetings!'
              : 'No meetings scheduled. Click "Schedule Meeting" to get started!'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedMeetings.map((meeting: Meeting) => (
            <MeetingCard
              key={meeting.id}
              meeting={meeting}
              contacts={contacts}
              onEdit={() => editMeeting(meeting)}
              onDelete={() => deleteMeeting(meeting.id)}
              onCompose={() => composeEmail(meeting)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Meeting Card Component
function MeetingCard({ meeting, contacts, onEdit, onDelete, onCompose }: any) {
  const participants = contacts.filter((c: Contact) => meeting.participantIds.includes(c.id));
  const dateTime = new Date(meeting.dateTime);
  const isVirtual = ['URL', 'Zoom', 'Discord', 'Facebook Messenger'].includes(meeting.locationType);

  const copyLink = () => {
    navigator.clipboard.writeText(meeting.shareableLink);
    alert('Shareable link copied to clipboard!');
  };

  const launchMeeting = () => {
    if (meeting.location) {
      window.open(meeting.location, '_blank');
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-2">{meeting.topic}</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-1">
            {dateTime.toLocaleString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: 'numeric',
              minute: '2-digit',
            })}
          </p>
          <p className="text-gray-600 dark:text-gray-400 flex items-center gap-2 mb-2">
            {meeting.locationType === 'Physical' && '📍'}
            {meeting.locationType === 'URL' && <ExternalLink size={16} />}
            {meeting.locationType === 'Zoom' && <Video size={16} />}
            {meeting.locationType === 'Discord' && <MessageCircle size={16} />}
            {meeting.locationType === 'Facebook Messenger' && <MessageCircle size={16} />}
            <span className="font-medium">{meeting.locationType}:</span>
            {isVirtual && meeting.location ? (
              <a
                href={meeting.location}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                {meeting.location}
              </a>
            ) : (
              <span>{meeting.location}</span>
            )}
          </p>
          <div className="flex items-center gap-2 mb-2">
            <Users size={16} className="text-gray-500 dark:text-gray-400" />
            <span className="text-gray-600 dark:text-gray-400">
              {participants.map((p: Contact) => p.name).join(', ')}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Share:</span>
            <code className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-gray-700 dark:text-gray-300">
              {meeting.shareableLink}
            </code>
            <button
              onClick={copyLink}
              className="p-1 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-700 rounded transition-colors"
              title="Copy link"
            >
              <Copy size={16} />
            </button>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {isVirtual && meeting.location && (
          <button
            onClick={launchMeeting}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors"
          >
            <ExternalLink size={16} />
            Launch
          </button>
        )}
        <button
          onClick={onCompose}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
        >
          <Mail size={16} />
          Compose Email
        </button>
        <button
          onClick={onEdit}
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center gap-2 transition-colors"
        >
          <Edit2 size={16} />
          Edit
        </button>
        <button
          onClick={onDelete}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2 transition-colors"
        >
          <Trash2 size={16} />
          Delete
        </button>
      </div>
    </div>
  );
}

// Meeting Form Component
function MeetingForm({ meeting, contacts, onSave, onCancel }: any) {
  const [formData, setFormData] = useState<Meeting>(
    meeting || {
      id: '',
      topic: '',
      dateTime: '',
      locationType: 'URL',
      location: '',
      participantIds: [],
      shareableLink: '',
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
          {meeting ? 'Edit Meeting' : 'Schedule Meeting'}
        </h2>
        <button type="button" onClick={onCancel} className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
          <X size={24} />
        </button>
      </div>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Topic *</label>
          <input
            type="text"
            required
            value={formData.topic}
            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date & Time *</label>
          <input
            type="datetime-local"
            required
            value={formData.dateTime}
            onChange={(e) => setFormData({ ...formData, dateTime: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Location Type *</label>
          <select
            value={formData.locationType}
            onChange={(e) => setFormData({ ...formData, locationType: e.target.value as any })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
          >
            <option value="Physical">Physical</option>
            <option value="URL">URL</option>
            <option value="Zoom">Zoom</option>
            <option value="Discord">Discord</option>
            <option value="Facebook Messenger">Facebook Messenger</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Location *</label>
          <input
            type={formData.locationType === 'Physical' ? 'text' : 'url'}
            required
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
            placeholder={formData.locationType === 'Physical' ? 'Address' : 'Meeting URL'}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Participants *</label>
          <select
            multiple
            required
            value={formData.participantIds}
            onChange={(e) => {
              const selected = Array.from(e.target.selectedOptions, (option) => option.value);
              setFormData({ ...formData, participantIds: selected });
            }}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100 min-h-[120px]"
          >
            {contacts.map((contact: Contact) => (
              <option key={contact.id} value={contact.id}>
                {contact.name} ({contact.email})
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Hold Ctrl/Cmd to select multiple</p>
        </div>
      </div>
      <div className="flex gap-3 mt-6">
        <button
          type="submit"
          className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {meeting ? 'Update' : 'Schedule'} Meeting
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

// Email Composer Component
function EmailComposer({ meeting, contacts, onClose }: any) {
  const [emailBody, setEmailBody] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const participants = contacts.filter((c: Contact) => meeting.participantIds.includes(c.id));
  const dateTime = new Date(meeting.dateTime);

  useEffect(() => {
    generateEmail();
  }, []);

  const generateEmail = async () => {
    setLoading(true);
    setError('');
    
    // Simulated AI generation - in production, this would call Gemini API
    setTimeout(() => {
      const participantSchedule = participants
        .map((p: Contact) => {
          const localTime = dateTime.toLocaleString('en-US', {
            timeZone: p.timezone,
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            timeZoneName: 'short',
          });
          return `${p.name}: ${localTime}`;
        })
        .join('\n');

      const aiBody = `Hi everyone,

I hope this message finds you well! I wanted to reach out to schedule our upcoming meeting about "${meeting.topic}".

I've arranged a time that should work across all of our timezones:

${participantSchedule}

Looking forward to our discussion!

Best regards`;

      setEmailBody(aiBody);
      setLoading(false);
    }, 1000);
  };

  const getBoilerplate = () => {
    const locationText = meeting.locationType === 'Physical' 
      ? meeting.location 
      : `${meeting.location}`;

    return `

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEETING DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Topic: ${meeting.topic}
Date & Time: ${dateTime.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })}
Location: ${locationText}

Join Link: ${meeting.shareableLink}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`;
  };

  const fullEmail = emailBody + getBoilerplate();
  const subject = `Meeting Invitation: ${meeting.topic}`;
  const toEmails = participants.map((p: Contact) => p.email).join(',');

  const openInEmail = () => {
    const isEdge = /Edg/.test(navigator.userAgent);
    
    if (isEdge) {
      const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(toEmails)}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(fullEmail)}`;
      window.open(gmailUrl, '_blank');
    } else {
      const mailtoLink = `mailto:${toEmails}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(fullEmail)}`;
      
      if (mailtoLink.length > 2000) {
        navigator.clipboard.writeText(`To: ${toEmails}\nSubject: ${subject}\n\n${fullEmail}`);
        alert('Email content is too long for mailto: link. The full email has been copied to your clipboard. Please paste it into your email client.');
      } else {
        window.location.href = mailtoLink;
      }
    }
  };

  const copyToClipboard = () => {
    const content = `To: ${toEmails}\nSubject: ${subject}\n\n${fullEmail}`;
    navigator.clipboard.writeText(content);
    alert('Email content copied to clipboard!');
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Compose Email Invitation</h2>
        <button onClick={onClose} className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200">
          <X size={24} />
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Generating email with AI...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 dark:bg-red-900 text-red-600 dark:text-red-200 p-4 rounded-lg mb-4">
          {error}
        </div>
      ) : (
        <>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Email Body (editable)
            </label>
            <textarea
              value={emailBody}
              onChange={(e) => setEmailBody(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100 min-h-[200px] font-mono text-sm"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Meeting Details (auto-generated)
            </label>
            <pre className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg text-sm overflow-x-auto text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
              {getBoilerplate()}
            </pre>
          </div>

          <div className="flex gap-3">
            <button
              onClick={openInEmail}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2 transition-colors"
            >
              <Send size={18} />
              Open in Email Client
            </button>
            <button
              onClick={copyToClipboard}
              className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center gap-2 transition-colors"
            >
              <Copy size={18} />
              Copy
            </button>
          </div>

          <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
            <p><strong>To:</strong> {toEmails}</p>
            <p><strong>Subject:</strong> {subject}</p>
          </div>
        </>
      )}
    </div>
  );
}
