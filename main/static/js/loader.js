<!-- static/loader.js -->
document.addEventListener('DOMContentLoaded', function () {
  const links = document.querySelectorAll('[data-page]');
  const content = document.getElementById('main-content');

  function loadPage(page) {
    fetch(`/container/${page}`)
      .then(res => res.text())
      .then(html => {
        content.innerHTML = html;
        if (page === 'truss') setTrussHandlers();
      });
  }

  links.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const page = this.dataset.page;
      if (page) loadPage(page);
    });
  });

  // 기본 페이지 로드
  loadPage('truss');
});

function setTrussHandlers() {
  const nodeInput = document.getElementById('nodeCsv');
  const elementInput = document.getElementById('elementCsv');

  nodeInput.addEventListener('change', () => {
    document.getElementById('nodeFileNameDisplay').textContent = nodeInput.files[0]?.name || '선택된 파일 없음';
  });
  elementInput.addEventListener('change', () => {
    document.getElementById('elementFileNameDisplay').textContent = elementInput.files[0]?.name || '선택된 파일 없음';
  });

  window.openModal = () => {
    document.getElementById('modal-notice')?.classList.add('active');
    document.getElementById('modal-backdrop')?.classList.add('active');
  };
  window.closeModal = () => {
    document.getElementById('modal-notice')?.classList.remove('active');
    document.getElementById('modal-backdrop')?.classList.remove('active');
  };
}
