import React from 'react';
import { useTheme } from '../context/ThemeContext';

/**
 * Example component demonstrating how to use the useTheme hook
 * This component shows the current theme and provides a button to toggle it
 */
export function ThemeExample() {
  const { theme, setTheme, isDark } = useTheme();

  const handleToggle = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <div className="card" style={{ marginTop: '20px' }}>
      <h3>Theme Example Component</h3>
      <p>
        <strong>Current Theme:</strong> {theme}
      </p>
      <p>
        <strong>Is Dark Mode:</strong> {isDark ? 'Yes' : 'No'}
      </p>
      <button className="btn btn-blue" onClick={handleToggle}>
        Toggle to {theme === 'light' ? 'Dark' : 'Light'} Mode
      </button>

      <hr style={{
        borderColor: 'var(--border-color)',
        margin: '15px 0'
      }} />

      <h4>How to use useTheme hook:</h4>
      <pre style={{
        backgroundColor: 'var(--bg-secondary)',
        padding: '10px',
        borderRadius: '4px',
        overflow: 'auto',
        fontSize: '0.85rem'
      }}>
{`import { useTheme } from '../context/ThemeContext';

function MyComponent() {
  const { theme, setTheme, isDark } = useTheme();

  return (
    <div>
      <p>Current theme: {theme}</p>
      <button onClick={() =>
        setTheme(theme === 'light' ? 'dark' : 'light')
      }>
        Toggle Theme
      </button>
    </div>
  );
}`}
      </pre>

      <h4>Available CSS Variables:</h4>
      <ul style={{ color: 'var(--text-secondary)' }}>
        <li><code>--bg-primary</code> - Main background color</li>
        <li><code>--bg-secondary</code> - Secondary background color</li>
        <li><code>--text-primary</code> - Main text color</li>
        <li><code>--text-secondary</code> - Secondary text color</li>
        <li><code>--border-color</code> - Border color</li>
        <li><code>--border-light</code> - Light border color</li>
        <li><code>--header-bg</code> - Header background color</li>
        <li><code>--input-bg</code> - Input background color</li>
        <li><code>--input-border</code> - Input border color</li>
      </ul>
    </div>
  );
}
