Design Document: Contact & Meeting Scheduler
1. Project Overview
The "Contact & Meeting Scheduler" is a local-first web application designed to be a personal relationship and time management tool. It allows users to maintain a detailed list of their contacts and schedule meetings with them. The application leverages AI to generate professional, timezone-aware email invitations, and provides robust data management options, including local persistence and file-based import/export.
Target Audience: Professionals, freelancers, and individuals who need a simple, private, and efficient way to manage their personal and professional contacts and schedule meetings without relying on a cloud-based subscription service.
Core Principles:
Local-First: All data is stored in the user's browser, ensuring privacy and offline availability.
User-Centric Design: The interface is clean, intuitive, and responsive, with a focus on streamlining common workflows.
AI-Enhanced: Gemini is used to assist with tedious tasks like writing emails, making the user more efficient.
Portable: Data can be easily backed up to and restored from a simple JSON file.
2. Core Features
2.1. Contact Management
A full CRUD (Create, Read, Update, Delete) system for managing contacts.
Contact Data Fields:
id: string (Unique identifier, e.g., via crypto.randomUUID())
name: string (Full name)
email: string (Primary email address)
timezone: string (IANA timezone, e.g., "America/New_York")
socials: object (Optional fields for social/professional accounts)
twitter: string (Username)
linkedin: string (Full profile URL)
github: string (Username)
messenger: string (Facebook Messenger username)
discord: string (Discord username, e.g., user#1234)
zoom: string (Zoom Personal Meeting ID or link)
2.2. Meeting Scheduling
A full CRUD system for managing meetings.
Meeting Data Fields:
id: string (Unique identifier)
topic: string (Meeting title)
dateTime: string (Full date and time in ISO 8601 format)
locationType: 'Physical' | 'URL' | 'Zoom' | 'Discord' | 'Facebook Messenger'
location: string (The address, URL, or link corresponding to the locationType)
participantIds: string[] (An array of contact ids)
shareableLink: string (A unique, generated URL for participants to view meeting details, e.g., https://[app-origin]/join?meetingId=[id])
2.3. AI-Powered Email Invitations
A modal-based composer to generate and send meeting invitations.
Gemini Integration: Use the Gemini API to generate the conversational body of an email invitation. The prompt should instruct the AI to:
Write a professional yet friendly message.
Mention the meeting topic.
Create a personalized schedule that shows the meeting time in each participant's local timezone.
Explicitly omit logistical details like location and join links, as these will be added programmatically.
Boilerplate Details: Automatically append a structured, non-editable section to the email body containing:
Topic
Date & Time (in the user's local format)
Location (with a clickable link if applicable)
A primary "Join Link" (the shareableLink).
Editable Body: The AI-generated portion of the email body must be editable within a <textarea>.
Email Client Integration:
An "Open in Email Client" button that constructs a mailto: link.
The link must include all participant emails in the To field, a pre-filled Subject, and the full email Body.
Edge Case Handling:
Detect if the browser is Microsoft Edge. If so, open a pre-filled Gmail compose URL in a new tab.
Check if the mailto: link exceeds 2000 characters. If so, prevent the default action, copy the full content to the clipboard, and show an alert informing the user to paste it manually.
Copy Functionality: A "Copy" button that copies a formatted string containing the To, Subject, and Body to the clipboard.
2.4. Data Persistence & Management
Local Storage: Use the browser's localStorage to persist all contacts and meetings.
Save to File: An export function that serializes the application's state (contacts and meetings) into a JSON file and initiates a download.
Restore from File: An import function that allows the user to select a JSON file, which is then parsed to overwrite the current application state.
Server Backup (Placeholder): Include UI elements for saving to and restoring from a server, which trigger simple alerts indicating they are placeholder functions.
3. UI/UX Design
3.1. General Layout & Style
Framework: React with TypeScript.
Styling: Tailwind CSS for a modern, utility-first approach.
Theme: A clean, professional theme with a defined color palette (primary, secondary, light, dark). Full support for both light and dark modes.
Responsiveness: The layout must be fully responsive, adapting gracefully from large desktop screens to mobile devices.
Header: A sticky header containing the application title, primary navigation (Contacts/Meetings), and data management icons.
3.2. Components
App: The root component managing the main state (contacts, meetings, currentView).
Header: Navigation tabs and action buttons for data management.
ContactList:
Displays contacts in a responsive grid of cards.
Each card shows the contact's name, email, timezone, and all social profiles with clickable icons/links.
Includes "Edit" and "Delete" buttons on each card.
A prominent "Add Contact" button.
MeetingList:
Displays meetings in a chronological list of cards.
Each card shows the topic, date/time, location (with appropriate icon), participant names, and the shareable link with a "Copy" button.
Action buttons on each card: "Launch" (for virtual meetings), "Compose Email", "Edit", and "Delete".
A prominent "Schedule Meeting" button, which is disabled if no contacts exist.
Modal: A reusable modal component for forms and dialogs.
ContactForm / MeetingForm: Forms housed within the Modal for creating and editing contacts and meetings. Use appropriate input types (datetime-local, email, url) and a multi-select for participants.
EmailComposer: The modal for generating, viewing, editing, and sending email invitations.
icons: A dedicated module for all SVG icons used in the application to ensure consistency.
3.3. User Flow
Onboarding: The user arrives at the Contacts view, which is initially empty.
Adding Contacts: The user clicks "Add Contact," fills out the form in the modal, and saves. The new contact appears on the screen.
Scheduling a Meeting: The user navigates to the Meetings view, clicks "Schedule Meeting," and fills out the form, selecting participants from the contact list.
Inviting Participants: The user clicks the "Compose Email" button on a meeting card. A modal appears, showing an AI-generated email.
Sending the Invitation: The user can edit the email if needed, then clicks "Open in Email Client" to send it.
Data Backup: The user clicks the "Save to File" icon to download a JSON backup of their data.
