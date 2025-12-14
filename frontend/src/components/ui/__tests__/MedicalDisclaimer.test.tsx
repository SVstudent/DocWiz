import React from 'react';
import { render, screen } from '@testing-library/react';
import { MedicalDisclaimer } from '../MedicalDisclaimer';

describe('MedicalDisclaimer', () => {
  describe('Variants', () => {
    it('should render default variant with icon', () => {
      render(<MedicalDisclaimer context="general" />);
      
      expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/for educational purposes only/i)).toBeInTheDocument();
    });

    it('should render compact variant', () => {
      render(<MedicalDisclaimer context="general" variant="compact" />);
      
      expect(screen.getByText(/Medical Disclaimer:/i)).toBeInTheDocument();
    });

    it('should render inline variant', () => {
      render(<MedicalDisclaimer context="general" variant="inline" />);
      
      expect(screen.getByText(/Note:/i)).toBeInTheDocument();
    });
  });

  describe('Contexts', () => {
    it('should render visualization context disclaimer', () => {
      render(<MedicalDisclaimer context="visualization" />);
      
      expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/AI-generated estimates/i)).toBeInTheDocument();
      expect(screen.getByText(/educational purposes only/i)).toBeInTheDocument();
    });

    it('should render cost context disclaimer', () => {
      render(<MedicalDisclaimer context="cost" />);
      
      expect(screen.getByText('Cost Estimate Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/approximations based on available data/i)).toBeInTheDocument();
    });

    it('should render procedure context disclaimer', () => {
      render(<MedicalDisclaimer context="procedure" />);
      
      expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/board-certified surgeon/i)).toBeInTheDocument();
    });

    it('should render comparison context disclaimer', () => {
      render(<MedicalDisclaimer context="comparison" />);
      
      expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/not guarantees of actual surgical outcomes/i)).toBeInTheDocument();
    });

    it('should render insurance context disclaimer', () => {
      render(<MedicalDisclaimer context="insurance" />);
      
      expect(screen.getByText('Important Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/informational purposes only/i)).toBeInTheDocument();
      expect(screen.getByText(/insurance provider/i)).toBeInTheDocument();
    });

    it('should render export context disclaimer', () => {
      render(<MedicalDisclaimer context="export" />);
      
      expect(screen.getByText('MEDICAL DISCLAIMER')).toBeInTheDocument();
      expect(screen.getByText(/AI-generated predictions/i)).toBeInTheDocument();
    });

    it('should render similar-cases context disclaimer', () => {
      render(<MedicalDisclaimer context="similar-cases" />);
      
      expect(screen.getByText('Privacy & Medical Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/anonymized to protect patient privacy/i)).toBeInTheDocument();
    });

    it('should render general context disclaimer', () => {
      render(<MedicalDisclaimer context="general" />);
      
      expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/educational purposes only/i)).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    it('should apply custom className', () => {
      const { container } = render(
        <MedicalDisclaimer context="general" className="custom-class" />
      );
      
      const disclaimer = container.querySelector('.custom-class');
      expect(disclaimer).toBeInTheDocument();
    });

    it('should have yellow background for default variant', () => {
      const { container } = render(<MedicalDisclaimer context="general" />);
      
      const disclaimer = container.querySelector('.bg-yellow-50');
      expect(disclaimer).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      const { container } = render(<MedicalDisclaimer context="general" />);
      
      const icon = container.querySelector('svg[aria-hidden="true"]');
      expect(icon).toBeInTheDocument();
    });

    it('should be readable by screen readers', () => {
      render(<MedicalDisclaimer context="visualization" />);
      
      // Check that important text is present and accessible
      expect(screen.getByText('Medical Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/AI-generated estimates/i)).toBeInTheDocument();
    });
  });

  describe('Content Requirements', () => {
    it('should always include disclaimer title', () => {
      const contexts: Array<'visualization' | 'cost' | 'procedure' | 'comparison' | 'insurance' | 'export' | 'similar-cases' | 'general'> = [
        'visualization',
        'cost',
        'procedure',
        'comparison',
        'insurance',
        'export',
        'similar-cases',
        'general',
      ];

      contexts.forEach((context) => {
        const { unmount } = render(<MedicalDisclaimer context={context} />);
        
        // Each context should have a title (either "Medical Disclaimer", "Important Disclaimer", etc.)
        const titleRegex = /disclaimer/i;
        expect(screen.getByText(titleRegex)).toBeInTheDocument();
        
        unmount();
      });
    });

    it('should include warning about consulting professionals', () => {
      render(<MedicalDisclaimer context="visualization" />);
      
      expect(screen.getByText(/qualified medical professional/i)).toBeInTheDocument();
    });

    it('should mention educational purposes for medical contexts', () => {
      render(<MedicalDisclaimer context="procedure" />);
      
      expect(screen.getByText(/educational purposes/i)).toBeInTheDocument();
    });
  });
});
