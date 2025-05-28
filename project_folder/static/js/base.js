console.log('=== BIRTHDAY APP SCRIPT LOADED ===');

// Helper function to escape HTML
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Function to load birthdays from API
async function loadBirthdays(tab = 'all') {
  console.log('Loading birthdays for tab:', tab);
  const container = document.getElementById('post-container');
  
  if (!container) {
    console.error('post-container not found!');
    return;
  }
  
  container.innerHTML = '<p>Loading birthdays...</p>';

  try {
    const response = await fetch(`/api/birthdays?tab=${encodeURIComponent(tab)}`);
    console.log('API response status:', response.status);
    
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

    const birthdays = await response.json();
    console.log('Loaded birthdays:', birthdays.length, 'items');

    if (birthdays.length === 0) {
      container.innerHTML = '<p>No birthdays found for this tab.</p>';
      return;
    }

    // Build HTML list of birthdays
    let html = '';
    birthdays.forEach(b => {
      html += `
        <article class="post">
            <div class="post-container">
                <div class="post-left">
                <h1>${escapeHtml(b.title)}</h1>
                <div class="about">by ${escapeHtml(b.username)}</div>
                </div>
                <div class="post-right">
                <p class="body">${escapeHtml(b.body || '')}</p>
                </div>
                <div class="post-right">
                <p class="date">${b.birthmonth}-${b.birthday}-${b.birthyear}</p>
                </div>
                ${CURRENT_USER_ID === b.author_id ? `
                <div class="post-edit">
                    <a class="edit-button" href="/update/${b.id}">✏️</a>
                </div>` : ''}
            </div>
        </article>
        <hr>`;
    });


    container.innerHTML = html;
    console.log('Birthdays loaded successfully');

  } catch (error) {
    console.error('Error loading birthdays:', error);
    container.innerHTML = `<p>Error loading birthdays: ${error.message}</p>`;
  }
}

// Make refresh function globally accessible
window.refreshBirthdays = loadBirthdays;

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM Content Loaded');
  
  // Get current tab from URL
  const urlParams = new URLSearchParams(window.location.search);
  const currentTab = urlParams.get('tab') || 'all';
  console.log('Current tab:', currentTab);

  // Load initial birthdays
  loadBirthdays(currentTab);

  // Handle tab clicks
  document.querySelectorAll('.tab-link').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      const newTab = e.target.dataset.tab;
      console.log('Tab clicked:', newTab);

      // Update URL without reload
      window.history.pushState(null, '', `/home?tab=${newTab}`);

      // Update active tab UI
      document.querySelectorAll('.tab-link').forEach(link => {
        link.classList.toggle('active', link.dataset.tab === newTab);
      });

      // Load birthdays for selected tab
      loadBirthdays(newTab);
    });
  });

  // Handle form submission
  const form = document.querySelector('#birthday-form');
  console.log('Form found:', !!form);
  
  if (form) {
    form.addEventListener('submit', async (e) => {
      console.log('=== FORM SUBMIT TRIGGERED ===');
      
      // CRITICAL: Prevent default form submission
      e.preventDefault();
      e.stopPropagation();
      
      console.log('Form submission prevented, processing...');

      // Get form data
      const title = form.querySelector('input[name="title"]')?.value?.trim();
      const body = form.querySelector('textarea[name="body"]')?.value?.trim();
      const day = form.querySelector('select[name="birthdate[day]"]')?.value;
      const month = form.querySelector('select[name="birthdate[month]"]')?.value;
      const year = form.querySelector('select[name="birthdate[year]"]')?.value;
      const tab = form.querySelector('input[name="tab"]')?.value || currentTab;

      console.log('Form data:', { title, body, day, month, year, tab });

      // Validation
      if (!title || !day || !month || !year) {
        alert('Please fill in all required fields');
        return;
      }

      // Disable submit button to prevent double submission
      const submitButton = form.querySelector('input[type="submit"]');
      const originalValue = submitButton.value;
      submitButton.disabled = true;
      submitButton.value = 'Saving...';

      try {
        const requestData = {
          title,
          body,
          birthdate: { day, month, year },
          tab
        };
        
        console.log('Sending POST request...');
        
        const response = await fetch('/home', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        });

        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);

        if (data.success) {
          console.log('SUCCESS: Birthday saved!');
          
          // Reset form
          form.reset();
          
          // Refresh the birthday list
          setTimeout(() => {
            loadBirthdays(tab);
          }, 100);
          
        } else {
          console.error('Server error:', data.error);
          alert('Error: ' + (data.error || 'Unknown error'));
        }
      } catch (error) {
        console.error('Request failed:', error);
        alert('Failed to submit: ' + error.message);
      } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.value = originalValue;
      }
    });
    
    console.log('Form event listener attached');
  } else {
    console.error('Form #birthday-form not found!');
  }

  // Highlight active tab
  document.querySelectorAll('.tab-link').forEach(el => {
    if (el.dataset.tab === currentTab) {
      el.classList.add('active');
    } else {
      el.classList.remove('active');
    }
  });
});
