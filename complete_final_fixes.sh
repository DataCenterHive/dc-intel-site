#!/bin/bash
# Complete final fixes for visual overhaul
# This script applies ALL remaining requirements

cd /mnt/c/Users/Yaseen/dc-intel-site-repo/dc-intel-site/docs

# 1. Remove last remaining alert()
sed -i "s/onclick=\"alert('Contact form coming soon! Email: contact@dc-intel.com')\"/onclick=\"showToast('Contact form coming soon! Email: contact@dc-intel.com', 'info')\"/g" index.html

echo "✅ Removed last alert() call"

# 2. Body background already fixed by Python script

# 3. Add toast CSS - will be inserted after modal-btn:hover
# This is complex, so we'll do it via Python

echo "Creating comprehensive final fixes..."

cat > apply_all_fixes.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add toast system CSS after modal-btn:hover
toast_css = '''
        /* Toast Notification System */
        #toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            gap: calc(var(--spacing-unit) * 1);
        }

        .toast {
            background: var(--bg-primary);
            border: 1px solid var(--border-default);
            border-radius: calc(var(--spacing-unit) * 1);
            padding: calc(var(--spacing-unit) * 2);
            min-width: 300px;
            max-width: 400px;
            box-shadow: var(--shadow-md);
            display: flex;
            align-items: flex-start;
            gap: calc(var(--spacing-unit) * 1.5);
            animation: slideIn 0.3s ease;
        }

        .toast.success { border-left: 4px solid var(--success); }
        .toast.error { border-left: 4px solid #dc2626; }
        .toast.info { border-left: 4px solid var(--brand-primary); }
        .toast.warning { border-left: 4px solid var(--warning); }

        .toast-message {
            flex: 1;
            font-size: 14px;
            line-height: 1.4;
            color: var(--text-primary);
        }

        .toast-close {
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 18px;
            line-height: 1;
            padding: 0;
        }

        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        /* Utility Classes */
        .btn-block {
            width: 100%;
            display: block;
        }

        .mt-20 {
            margin-top: calc(var(--spacing-unit) * 2.5);
        }

        /* Pricing Card Classes */
        .pricing-card {
            border: 2px solid var(--border-emphasis);
            padding: calc(var(--spacing-unit) * 3);
            background: var(--bg-primary);
            position: relative;
            border-radius: calc(var(--spacing-unit) * 1);
        }

        .pricing-card__header {
            background: var(--text-primary);
            color: #ffffff;
            border: none;
            padding: calc(var(--spacing-unit) * 1);
            text-align: center;
            margin: calc(var(--spacing-unit) * -3) calc(var(--spacing-unit) * -3) calc(var(--spacing-unit) * 2.5);
            font-weight: bold;
            letter-spacing: 1px;
        }

        .pricing-card__price {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: calc(var(--spacing-unit) * 1);
        }

        .pricing-card__price span {
            font-size: 14px;
            font-weight: normal;
        }

        .data-freshness {
            color: var(--text-secondary);
            font-size: 12px;
            margin-bottom: calc(var(--spacing-unit) * 1);
            font-weight: 500;
        }

        .news-card {
            background: var(--bg-primary);
            border: 1px solid var(--border-default);
            border-radius: calc(var(--spacing-unit) * 1);
            padding: calc(var(--spacing-unit) * 3);
            margin-bottom: calc(var(--spacing-unit) * 2);
            box-shadow: var(--shadow-sm);
            transition: box-shadow 0.2s ease;
        }

        .news-card:hover {
            box-shadow: var(--shadow-md);
        }

        .news-card__headline {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: calc(var(--spacing-unit) * 1);
            color: var(--text-primary);
        }

        .news-card__summary {
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-secondary);
            margin-bottom: calc(var(--spacing-unit) * 1.5);
        }

        .news-card__meta {
            font-size: 12px;
            color: var(--text-secondary);
            display: flex;
            gap: calc(var(--spacing-unit) * 2);
        }
'''

# Insert toast CSS after .modal-btn:hover
html = html.replace(
    '        .modal-btn:hover {\n            background: var(--brand-hover);\n            border-color: var(--brand-hover);\n            transform: translateY(-1px);\n            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);\n        }',
    '        .modal-btn:hover {\n            background: var(--brand-hover);\n            border-color: var(--brand-hover);\n            transform: translateY(-1px);\n            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);\n        }\n' + toast_css
)

# Add toast container HTML before closing </body>
toast_html = '    <div id="toast-container"></div>\n'
html = re.sub(r'(\s*</body>)', r'\n' + toast_html + r'\1', html)

# Add toast JavaScript functions before closing </script>
toast_js = '''
        // Toast notification system
        function showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            if (!container) return;

            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `
                <div class="toast-message">${escapeHtml(message)}</div>
                <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
            `;

            container.appendChild(toast);

            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.style.animation = 'slideIn 0.3s ease reverse';
                    setTimeout(() => toast.remove(), 300);
                }
            }, 5000);
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Upgrade modal for tier-gated features
        function showUpgradeModal(feature, requiredTier) {
            const messages = {
                'study-guide': `This content requires a ${requiredTier} subscription. Upgrade to access study guides.`,
                'news-archive': `News Archive is an Enterprise-only feature. Upgrade to access the complete historical archive.`
            };

            const modal = document.getElementById('exportLimitModal');
            if (modal) {
                // Reuse export modal with custom message
                const content = modal.querySelector('.modal-content h2');
                if (content) {
                    const originalText = content.textContent;
                    content.textContent = `Upgrade to ${requiredTier}`;
                    modal.classList.add('active');

                    // Restore original text when closed
                    const closeBtn = modal.querySelector('.modal-close');
                    const restoreOriginal = () => {
                        content.textContent = originalText;
                        closeBtn.removeEventListener('click', restoreOriginal);
                    };
                    closeBtn.addEventListener('click', restoreOriginal);
                }
            } else {
                showToast(messages[feature] || `This feature requires ${requiredTier} tier.`, 'info');
            }
        }
'''

# Find last </script> and insert toast JS before it
last_script_close = html.rfind('</script>')
if last_script_close > 0:
    html = html[:last_script_close] + '\n' + toast_js + '\n        ' + html[last_script_close:]

# Update Basic tier button to "START TRIAL" with modal
html = re.sub(
    r'<a href="mailto:sales@datacenterhive\.com\?subject=Basic%20Tier%20Inquiry"\s+class="btn-primary"\s+style="width: 100%; margin-top: 20px; display: block;">\s*CONTACT SALES\s*</a>',
    '<a href="javascript:void(0)" class="btn-primary btn-block mt-20" onclick="showTrialModal()">START TRIAL</a>',
    html
)

# Add trial modal function
trial_modal_js = '''
        function showTrialModal() {
            showToast('Trial access: Create a free account to start your 14-day trial with full Basic tier features.', 'info');
            setTimeout(() => {
                const registerLink = document.querySelector('a[href="auth/register.html"]');
                if (registerLink) registerLink.click();
            }, 2000);
        }
'''
html = html.replace(toast_js, toast_js + trial_modal_js)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Added toast system CSS, HTML, and JavaScript")
print("✅ Added pricing card utility classes")
print("✅ Updated Basic tier CTA to 'START TRIAL'")
PYTHON_EOF

python3 apply_all_fixes.py

echo ""
echo "=== FINAL VERIFICATION ==="
echo "alert() calls remaining: $(grep -c 'alert(' index.html)"
echo "#f5f5dc (beige) remaining: $(grep -c '#f5f5dc' index.html)"
echo "Georgia font remaining: $(grep -c 'font-family.*Georgia' index.html || echo 0)"
echo "COMING SOON remaining: $(grep -c 'COMING SOON' index.html)"

echo ""
echo "✅ All fixes applied!"
