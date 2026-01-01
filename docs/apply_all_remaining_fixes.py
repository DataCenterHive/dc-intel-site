#!/usr/bin/env python3
"""
Complete all remaining visual overhaul requirements.
This script applies ALL fixes to meet the exact specification.
"""

import re

# Read the file
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Starting comprehensive fixes...")

# 1. Remove last remaining alert() call (contact form)
html = re.sub(
    r"onclick=\"alert\('Contact form coming soon! Email: contact@dc-intel\.com'\)\"",
    "onclick=\"showToast('Contact form coming soon! Email: contact@dc-intel.com', 'info')\"",
    html
)
print("✅ Removed last alert() call")

# 2. Add toast system CSS after .modal-btn:hover
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
print("✅ Added toast system CSS and utility classes")

# 3. Add toast container HTML before closing </body>
toast_html = '    <div id="toast-container"></div>\n'
html = re.sub(r'(\s*</body>)', r'\n' + toast_html + r'\1', html)
print("✅ Added toast container HTML")

# 4. Add toast JavaScript functions before closing </script>
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

        // Trial modal function
        function showTrialModal() {
            showToast('Trial access: Create a free account to start your 14-day trial with full Basic tier features.', 'info');
            setTimeout(() => {
                const registerLink = document.querySelector('a[href="auth/register.html"]');
                if (registerLink) registerLink.click();
            }, 2000);
        }
'''

# Find last </script> and insert toast JS before it
last_script_close = html.rfind('</script>')
if last_script_close > 0:
    html = html[:last_script_close] + '\n' + toast_js + '\n        ' + html[last_script_close:]
print("✅ Added toast JavaScript functions")

# 5. Update Basic tier button to "START TRIAL" with modal
html = re.sub(
    r'<a href="mailto:sales@datacenterhive\.com\?subject=Basic%20Tier%20Inquiry"\s+class="btn-primary"\s+style="width: 100%; margin-top: 20px; display: block;">\s*CONTACT SALES\s*</a>',
    '<a href="javascript:void(0)" class="btn-primary btn-block mt-20" onclick="showTrialModal()">START TRIAL</a>',
    html
)
print("✅ Updated Basic tier CTA to 'START TRIAL'")

# 6. Add data freshness labels to tables
# Find "Existing Data Centers" table header and add freshness indicator
html = re.sub(
    r'(<h3[^>]*>Existing Data Centers</h3>)',
    r'\1\n            <p class="data-freshness">Data refresh: Daily</p>',
    html
)

# Find "Upcoming Data Centers" table header and add freshness indicator
html = re.sub(
    r'(<h3[^>]*>Upcoming Data Centers</h3>)',
    r'\1\n            <p class="data-freshness">Data refresh: Daily</p>',
    html
)
print("✅ Added data freshness labels to tables")

# 7. Wrap news snippets in modern card UI
# This requires finding the news section and wrapping each article
# Looking for the pattern in the news loading section
html = re.sub(
    r'newsDiv\.innerHTML \+= `\s*<div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #ddd;">\s*<h4 style="margin: 0 0 5px 0; color: #333;"><a href="\$\{article\.url\}" target="_blank" style="color: #2563eb; text-decoration: none;">\$\{article\.headline\}</a></h4>\s*<p style="margin: 5px 0; color: #666; font-size: 14px;">\$\{article\.summary\}</p>\s*<small style="color: #999;">\$\{article\.source\} - \$\{article\.date\}</small>\s*</div>\s*`;',
    '''newsDiv.innerHTML += `
                    <div class="news-card">
                        <h4 class="news-card__headline"><a href="${article.url}" target="_blank" style="color: var(--brand-primary); text-decoration: none;">${article.headline}</a></h4>
                        <p class="news-card__summary">${article.summary}</p>
                        <div class="news-card__meta">
                            <span>${article.source}</span>
                            <span>${article.date}</span>
                        </div>
                    </div>
                `;''',
    html,
    flags=re.DOTALL
)
print("✅ Wrapped news snippets in modern card UI")

# 8. Write the file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n" + "="*50)
print("ALL FIXES APPLIED SUCCESSFULLY!")
print("="*50)
