import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import re

# Set style
plt.style.use('bmh')

class ChartGenerator:
    def __init__(self, data):
        self.data = data
        self.charts = {}

    def generate_all(self):
        """Generates all possible charts based on available data"""
        try:
            if self._has_grant_data():
                self.charts['grant_amount'] = self._create_grant_chart()
            
            if self._has_eligibility_data():
                self.charts['eligibility'] = self._create_eligibility_chart()
                
            if self._has_document_data():
                self.charts['documents'] = self._create_documents_chart()
                
            return self.charts
        except Exception as e:
            print(f"Chart generation error: {e}")
            return {}

    def _fig_to_base64(self, fig):
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close(fig)
        return "data:image/png;base64," + base64.b64encode(image_png).decode('utf-8')

    # --- Data Helpers ---
    
    def _extract_amount(self):
        """Robust extraction of scholarship amount from various JSON structures"""
        amount = 0
        label = "Scholarship Amount"
        
        # Check 1: 'scholarship_benefits' dict
        benefits = self.data.get('scholarship_benefits', {})
        if isinstance(benefits, dict):
            amt_str = benefits.get('amount', '')
            if not amt_str and 'benefit_structure_table' in benefits:
                # Try to grab first amount from table rows
                rows = benefits['benefit_structure_table'].get('table_rows', [])
                if rows:
                    amt_str = str(rows[0][-1]) # Last column usually has amount
            
            if amt_str:
                amount = self._parse_currency(str(amt_str))
                label = str(amt_str).split('(')[0].strip()[:20]

        # Check 2: 'grant_amount' (Used in Kanyashree)
        if amount == 0 and 'grant_amount' in self.data:
            ga = self.data['grant_amount']
            if isinstance(ga, dict):
                amount = self._parse_currency(ga.get('amount', '0'))
                label = ga.get('amount', str(amount))
            else:
                amount = self._parse_currency(str(ga))
                label = "Grant"

        return amount, label

    def _parse_currency(self, text):
        """Extracts the first large number found in text"""
        if not text: return 0
        # Remove commas and search for numbers
        clean = text.replace(',', '')
        matches = re.findall(r'\d+', clean)
        if matches:
            # Return the largest number found (likely the total amount)
            return max([int(m) for m in matches])
        return 0

    # --- Checkers ---

    def _has_grant_data(self):
        amt, _ = self._extract_amount()
        return amt > 0

    def _has_eligibility_data(self):
        # Checks for income criteria or general eligibility
        criteria = self.data.get('eligibility_criteria', {})
        return isinstance(criteria, dict) and ('income_criteria' in criteria or 'age_criteria' in criteria)

    def _has_document_data(self):
        docs = self.data.get('documents_required', []) or self.data.get('required_documents', [])
        return len(docs) > 0

    # --- Generators ---

    def _create_grant_chart(self):
        amount, label = self._extract_amount()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Create a single horizontal bar
        bars = ax.barh(['Grant'], [amount], color='#4CAF50', height=0.5)
        
        # Label the bar with the formatted text
        ax.bar_label(bars, labels=[label], padding=8, fontsize=12, fontweight='bold')
        
        ax.set_title('Financial Benefit', pad=20)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.get_xaxis().set_visible(False)
        
        return self._fig_to_base64(fig)

    def _create_eligibility_chart(self):
        """Visualizes Income Limit vs Age Limit or similar metrics"""
        criteria = self.data.get('eligibility_criteria', {})
        
        # Extract Income
        income_limit = 0
        income_text = "N/A"
        if 'income_criteria' in criteria:
            inc = criteria['income_criteria']
            if isinstance(inc, dict):
                val = inc.get('maximum_family_income', '') or inc.get('annual_family_income_limit', '')
                income_limit = self._parse_currency(str(val))
                income_text = f"₹{income_limit:,}" if income_limit else "See Details"

        # Create a visual summary
        fig, ax = plt.subplots(figsize=(8, 2))
        ax.axis('off')
        
        # Draw Income Box
        ax.text(0.5, 0.5, f"Max Family Income\n{income_text}", 
                ha='center', va='center', fontsize=14, 
                bbox=dict(boxstyle="round,pad=1", fc="#E3F2FD", ec="#2196F3"))

        return self._fig_to_base64(fig)

    def _create_documents_chart(self):
        """Creates a visual checklist of documents"""
        docs = self.data.get('documents_required', []) or self.data.get('required_documents', [])
        
        # Handle dict format (e.g. {fresh: [], renewal: []})
        if isinstance(docs, dict):
            # Just grab the first list we find
            for key in docs:
                if isinstance(docs[key], list):
                    docs = docs[key]
                    break
        
        # If it's still not a list or empty
        if not isinstance(docs, list) or not docs:
            return None

        # Take top 5 documents
        docs = docs[:5] 
        
        fig, ax = plt.subplots(figsize=(8, len(docs) * 0.8))
        ax.axis('off')
        
        for i, doc in enumerate(docs):
            doc_text = doc if isinstance(doc, str) else str(doc).split(':')[0]
            # Truncate long text
            if len(doc_text) > 50: doc_text = doc_text[:47] + "..."
            ax.text(0.05, 1 - (i * 0.2), f"✔ {doc_text}", fontsize=11, ha='left')
            
        ax.set_title("Key Documents Required", loc='left', pad=10, fontsize=12, fontweight='bold')
            
        return self._fig_to_base64(fig)


def generate_scholarship_charts(data):
    generator = ChartGenerator(data)
    return generator.generate_all()