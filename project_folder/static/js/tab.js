document.addEventListener("DOMContentLoaded", function () {
  const links = document.querySelectorAll(".tab-link");
  const container = document.getElementById("post-container");

  function updateActiveTab(tabName) {
    links.forEach(link => {
      if (link.getAttribute("data-tab") === tabName) {
        link.classList.add("active-tab");
      } else {
        link.classList.remove("active-tab");
      }
    });
  }

  links.forEach(link => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const tab = this.getAttribute("data-tab");
      const url = `/home?tab=${tab}`;

      fetch(url)
        .then(res => res.text())
        .then(html => {
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");

          const newHeader = doc.querySelector("header");
          if (newHeader) {
            document.querySelector("header").innerHTML = newHeader.innerHTML;
          }

          const newContent = doc.getElementById("post-container");
          if (newContent) {
            container.innerHTML = newContent.innerHTML;
            history.pushState({}, "", url);
            updateActiveTab(tab);
          }
        })
        .catch(err => {
          console.error("Tab switch failed:", err);
        });
    });
  });

  // Set initial active tab based on current URL
  const urlParams = new URLSearchParams(window.location.search);
  const currentTab = urlParams.get("tab");
  if (currentTab) {
    updateActiveTab(currentTab);
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const tabLinks = document.querySelectorAll(".tab-link");

  tabLinks.forEach(link => {
    link.addEventListener("click", function (e) {
      e.preventDefault(); // Prevent anchor reload

      // Remove .active from all tabs
      tabLinks.forEach(tab => tab.classList.remove("active"));

      // Add .active to clicked tab
      this.classList.add("active");

      // Optional: Handle dynamic content update
      const selectedTab = this.dataset.tab;
      updateTabContent(selectedTab); // You define this function if needed
    });
  });
});

