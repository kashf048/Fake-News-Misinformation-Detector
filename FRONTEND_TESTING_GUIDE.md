# Frontend Testing Guide

## Component Testing

### Test Setup

```bash
# Install testing dependencies
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom

# Create vitest config
npm install --save-dev vitest jsdom
```

### Component Test Examples

#### FileUpload Component Test

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FileUpload from '@/components/FileUpload';

describe('FileUpload Component', () => {
  it('renders upload input', () => {
    render(<FileUpload onImageSelect={vi.fn()} />);
    expect(screen.getByText(/upload/i)).toBeInTheDocument();
  });

  it('handles file selection', () => {
    const handleSelect = vi.fn();
    render(<FileUpload onImageSelect={handleSelect} />);
    
    const input = screen.getByRole('input');
    fireEvent.change(input, {
      target: { files: [new File(['test'], 'test.jpg')] }
    });
    
    expect(handleSelect).toHaveBeenCalled();
  });

  it('validates file type', () => {
    render(<FileUpload onImageSelect={vi.fn()} />);
    const input = screen.getByRole('input');
    
    fireEvent.change(input, {
      target: { files: [new File(['test'], 'test.txt')] }
    });
    
    expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
  });
});
```

#### ResultCard Component Test

```typescript
describe('ResultCard Component', () => {
  const mockResult = {
    _id: '123',
    headline: 'Test headline',
    prediction: 'Fake',
    confidence: 0.85,
    similarity: 0.42,
    explanation: 'This is a test',
    fact_checks: [],
    created_at: new Date().toISOString(),
  };

  it('displays prediction', () => {
    render(<ResultCard result={mockResult} />);
    expect(screen.getByText('Fake')).toBeInTheDocument();
  });

  it('displays confidence score', () => {
    render(<ResultCard result={mockResult} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('displays explanation', () => {
    render(<ResultCard result={mockResult} />);
    expect(screen.getByText('This is a test')).toBeInTheDocument();
  });
});
```

### Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run tests with coverage
npm run test -- --coverage

# Run specific test file
npm run test -- FileUpload.test.tsx

# Run tests matching pattern
npm run test -- --grep "Component"
```

---

## Integration Testing

### API Service Testing

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { apiService } from '@/services/api';
import axios from 'axios';

vi.mock('axios');

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('analyzes headline', async () => {
    const mockResponse = {
      data: {
        _id: '123',
        prediction: 'Fake',
        confidence: 0.85,
      }
    };

    vi.mocked(axios.post).mockResolvedValue(mockResponse);

    const result = await apiService.analyze({
      headline: 'Test headline'
    });

    expect(result.prediction).toBe('Fake');
  });

  it('handles API errors', async () => {
    vi.mocked(axios.post).mockRejectedValue(
      new Error('API Error')
    );

    await expect(
      apiService.analyze({ headline: 'Test' })
    ).rejects.toThrow('API Error');
  });
});
```

---

## E2E Testing with Cypress

### Setup

```bash
# Install Cypress
npm install --save-dev cypress

# Open Cypress
npx cypress open
```

### Test Examples

#### Analyze Flow

```typescript
describe('Analysis Flow', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');
  });

  it('analyzes headline successfully', () => {
    // Type headline
    cy.get('input[placeholder="Enter headline"]')
      .type('Breaking news about technology');

    // Click analyze button
    cy.get('button').contains('Analyze Now').click();

    // Wait for result
    cy.get('[data-testid="result-card"]', { timeout: 10000 })
      .should('be.visible');

    // Verify result displayed
    cy.get('[data-testid="prediction"]')
      .should('contain', /Fake|Real|Misleading/);
  });

  it('displays error for empty headline', () => {
    cy.get('button').contains('Analyze Now').click();
    cy.get('[data-testid="error-message"]')
      .should('contain', 'Please enter a headline');
  });
});
```

#### History Flow

```typescript
describe('History Flow', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');
  });

  it('navigates to history page', () => {
    cy.get('nav').contains('History').click();
    cy.url().should('include', '/history');
  });

  it('filters history by prediction', () => {
    cy.visit('http://localhost:5173/history');
    
    cy.get('select[name="prediction"]')
      .select('Fake');

    cy.get('[data-testid="history-item"]')
      .each(($item) => {
        cy.wrap($item)
          .should('contain', 'Fake');
      });
  });

  it('deletes analysis', () => {
    cy.visit('http://localhost:5173/history');
    
    cy.get('[data-testid="delete-button"]')
      .first()
      .click();

    cy.get('[data-testid="confirm-delete"]')
      .click();

    cy.get('[data-testid="success-message"]')
      .should('contain', 'deleted successfully');
  });
});
```

#### Analytics Flow

```typescript
describe('Analytics Flow', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');
  });

  it('displays analytics dashboard', () => {
    cy.get('nav').contains('Analytics').click();
    cy.url().should('include', '/analytics');

    // Check stats cards
    cy.get('[data-testid="total-analyses"]')
      .should('be.visible');
    cy.get('[data-testid="fake-count"]')
      .should('be.visible');
    cy.get('[data-testid="real-count"]')
      .should('be.visible');
  });

  it('displays charts', () => {
    cy.visit('http://localhost:5173/analytics');

    // Check pie chart
    cy.get('[data-testid="distribution-chart"]')
      .should('be.visible');

    // Check bar chart
    cy.get('[data-testid="trends-chart"]')
      .should('be.visible');
  });
});
```

### Running Cypress Tests

```bash
# Open Cypress UI
npx cypress open

# Run tests headless
npx cypress run

# Run specific test file
npx cypress run --spec "cypress/e2e/analysis.cy.ts"

# Run with specific browser
npx cypress run --browser chrome
```

---

## Performance Testing

### Lighthouse Audit

```bash
# Install Lighthouse
npm install -g lighthouse

# Run audit
lighthouse http://localhost:5173 --view

# Generate report
lighthouse http://localhost:5173 --output-path ./report.html
```

### Bundle Analysis

```bash
# Analyze bundle
npm run build -- --analyze

# View bundle report
open dist/stats.html
```

### Performance Metrics

```typescript
// Measure component render time
import { performance } from 'perf_hooks';

const start = performance.now();
render(<Home />);
const end = performance.now();
console.log(`Render time: ${end - start}ms`);
```

---

## Accessibility Testing

### axe Testing

```bash
# Install axe
npm install --save-dev @axe-core/react

# Run accessibility tests
npm run test:a11y
```

### Manual Accessibility Testing

```bash
# Check keyboard navigation
# Tab through all interactive elements

# Check color contrast
# Use browser DevTools color contrast checker

# Check screen reader
# Use NVDA (Windows) or VoiceOver (Mac)

# Check ARIA labels
# Inspect elements for proper ARIA attributes
```

---

## Visual Regression Testing

### Percy Integration

```bash
# Install Percy
npm install --save-dev @percy/cli @percy/cypress

# Run with Percy
npx percy exec -- npx cypress run
```

---

## Test Coverage

### Generate Coverage Report

```bash
# Generate coverage
npm run test -- --coverage

# View coverage report
open coverage/index.html
```

### Coverage Goals

- Statements: > 80%
- Branches: > 75%
- Functions: > 80%
- Lines: > 80%

---

## Debugging Tests

### Debug Mode

```bash
# Run tests in debug mode
npm run test -- --inspect-brk

# Use Chrome DevTools
# chrome://inspect
```

### Console Logging

```typescript
it('should work', () => {
  console.log('Debug info');
  expect(true).toBe(true);
});
```

### Screen Debugging

```typescript
import { screen, debug } from '@testing-library/react';

it('should display text', () => {
  render(<Component />);
  debug(); // Prints DOM
  screen.logTestingPlaygroundURL(); // Prints testing playground URL
});
```

---

## Test Checklist

- [ ] All components have unit tests
- [ ] All pages have integration tests
- [ ] E2E tests cover main flows
- [ ] API service tests pass
- [ ] Coverage > 80%
- [ ] No accessibility violations
- [ ] No performance regressions
- [ ] All tests pass in CI/CD

---

**Frontend Testing Guide Version**: 1.0.0
**Last Updated**: January 2024
