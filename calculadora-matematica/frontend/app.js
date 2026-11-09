/* ============================================================
   MathLab — lógica da aplicação (JavaScript puro)
   Lê o catálogo do backend, renderiza categorias/formulários
   e devolve os resultados calculados pela API Flask.
   ============================================================ */

(() => {
  "use strict";

  const STORAGE_KEY = "mathlab.categoria.ativa";

  const state = {
    categories: [],
    operations: [],
    activeCategory: null,
    search: "",
    current: null,
  };

  const els = {
    stats: document.getElementById("topbar-stats"),
    categories: document.getElementById("categories"),
    search: document.getElementById("search"),
    categoryName: document.getElementById("category-name"),
    categoryDescription: document.getElementById("category-description"),
    searchInfo: document.getElementById("search-info"),
    operations: document.getElementById("operations"),
    empty: document.getElementById("empty"),
    modal: document.getElementById("modal"),
    modalClose: document.getElementById("modal-close"),
    modalTag: document.getElementById("modal-tag"),
    modalTitle: document.getElementById("modal-title"),
    modalDesc: document.getElementById("modal-desc"),
    form: document.getElementById("calc-form"),
    fields: document.getElementById("form-fields"),
    submitBtn: document.getElementById("submit-btn"),
    resetBtn: document.getElementById("reset-btn"),
    result: document.getElementById("result"),
  };

  let lastFocused = null; // elemento que tinha o foco antes de abrir o modal

  /* ------------------------------------------------------ validação */

  // Aceita "12", "12,5", ".5", "-3", "1e-5" (o backend aceita o resto)
  const NUMBER_RE = /^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)(?:[eE][+-]?\d+)?$/;

  const isNumeric = (text) => NUMBER_RE.test(text);

  function validateFraction(value, label) {
    const text = value.replace(/,/g, ".").trim();
    const parts = text.split(/\s+/);

    if (parts.length > 2) {
      return `“${value}” não é uma fração válida em “${label}”.`;
    }

    let target = text;
    if (parts.length === 2) {
      // número misto: "2 1/4"
      if (!isNumeric(parts[0])) {
        return `“${parts[0]}” não é um número válido em “${label}”.`;
      }
      target = parts[1];
    }

    if (target.includes("/")) {
      const [num, den] = target.split("/");
      if (!num || !den || !isNumeric(num) || !isNumeric(den)) {
        return `“${value}” não é uma fração válida em “${label}”.`;
      }
      if (Number(den) === 0) {
        return `O denominador de “${label}” não pode ser zero.`;
      }
      return null;
    }

    return isNumeric(target) ? null : `“${value}” não é um número válido em “${label}”.`;
  }

  // Devolve uma mensagem em português ou null quando o valor é aceitável.
  function validateField(field, value) {
    const required = field.required !== false;
    const label = field.label || field.name;

    if (!value) {
      return required ? `Preenche o campo “${label}”.` : null;
    }

    switch (field.type) {
      case "number":
        if (value.includes("/")) return validateFraction(value, label);
        return isNumeric(value) ? null : `“${value}” não é um número válido em “${label}”.`;

      case "integer": {
        if (!isNumeric(value)) {
          return `“${value}” não é um número válido em “${label}”.`;
        }
        const n = Number(value.replace(",", "."));
        return Number.isInteger(n)
          ? null
          : `O campo “${label}” tem de ser um número inteiro (recebido: ${value}).`;
      }

      case "list": {
        const parts = value.split(/[,;\s]+/).filter(Boolean);
        if (!parts.length) return required ? `Preenche o campo “${label}”.` : null;
        const invalid = parts.find((part) => !isNumeric(part));
        return invalid
          ? `“${invalid}” não é um número válido na lista “${label}”.`
          : null;
      }

      case "fraction":
        return validateFraction(value, label);

      case "select": {
        const options = (field.options || []).map((option) => String(option.value));
        return options.includes(value) ? null : `Escolhe uma opção em “${label}”.`;
      }

      case "expression":
        return value ? null : `Escreve uma expressão em “${label}”.`;

      default:
        return null; // campos de texto: o backend valida os obrigatórios
    }
  }

  function markInvalid(control, message) {
    control.classList.add("invalid");
    control.setAttribute("aria-invalid", "true");
    control.title = message;
  }

  function clearInvalid(control) {
    control.classList.remove("invalid");
    control.removeAttribute("aria-invalid");
    if (control.dataset.hint) control.title = control.dataset.hint;
    else control.removeAttribute("title");
  }

  /* ------------------------------------------------------------ init */

  async function init() {
    try {
      const response = await fetch("/api/operations");
      if (!response.ok) throw new Error("HTTP " + response.status);
      const data = await response.json();

      state.categories = data.categories;
      state.operations = data.operations;

      const saved = localStorage.getItem(STORAGE_KEY);
      state.activeCategory = state.categories.some((c) => c.id === saved)
        ? saved
        : state.categories[0].id;

      els.stats.textContent =
        `${state.operations.length} operações · ${state.categories.length} matérias`;

      renderCategories();
      renderOperations();
    } catch (error) {
      els.operations.innerHTML =
        `<div class="empty"><span class="empty-icon">🔌</span>
           <p><strong>Não foi possível ligar ao servidor.</strong></p>
           <p>Arranca o backend com <code>python backend/app.py</code> e recarrega a página.</p>
         </div>`;
      els.categoryName.textContent = "Erro de ligação";
      console.error(error);
    }
  }

  /* ------------------------------------------------------ categorias */

  function renderCategories() {
    els.categories.innerHTML = "";

    state.categories.forEach((category) => {
      const count = state.operations.filter((op) => op.category === category.id).length;

      const button = document.createElement("button");
      button.type = "button";
      button.className = "category-btn" + (category.id === state.activeCategory ? " active" : "");
      button.dataset.category = category.id;

      const name = document.createElement("span");
      name.textContent = category.name;

      const badge = document.createElement("span");
      badge.className = "category-count";
      badge.textContent = count;

      button.append(name, badge);
      button.addEventListener("click", () => selectCategory(category.id));
      els.categories.appendChild(button);
    });
  }

  function selectCategory(categoryId) {
    state.activeCategory = categoryId;
    localStorage.setItem(STORAGE_KEY, categoryId);

    if (state.search) {
      state.search = "";
      els.search.value = "";
    }

    renderCategories();
    renderOperations();
  }

  /* ------------------------------------------------------- operações */

  function visibleOperations() {
    const query = state.search.trim().toLowerCase();

    if (!query) {
      return state.operations.filter((op) => op.category === state.activeCategory);
    }

    return state.operations.filter((op) => {
      const category = state.categories.find((c) => c.id === op.category);
      const haystack = [op.name, op.description, category ? category.name : ""]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    });
  }

  function renderOperations() {
    const category = state.categories.find((c) => c.id === state.activeCategory);
    const searching = state.search.trim().length > 0;
    const operations = visibleOperations();

    els.categoryName.textContent = searching ? "Resultados da pesquisa" : category.name;
    els.categoryDescription.textContent = searching
      ? `A procurar por “${state.search.trim()}” em todas as matérias.`
      : category.description;

    if (searching) {
      els.searchInfo.hidden = false;
      els.searchInfo.textContent =
        `${operations.length} operação(ões) encontrada(s).`;
    } else {
      els.searchInfo.hidden = true;
    }

    els.operations.innerHTML = "";
    els.empty.hidden = operations.length > 0;

    operations.forEach((operation) => {
      const categoryOf = state.categories.find((c) => c.id === operation.category);

      const card = document.createElement("button");
      card.type = "button";
      card.className = "op-card";

      const tag = document.createElement("span");
      tag.className = "op-card-tag";
      tag.textContent = categoryOf ? categoryOf.name : operation.category;

      const name = document.createElement("span");
      name.className = "op-card-name";
      name.textContent = operation.name;

      const description = document.createElement("span");
      description.className = "op-card-desc";
      description.textContent = operation.description;

      card.append(tag, name, description);
      card.addEventListener("click", () => openOperation(operation));
      els.operations.appendChild(card);
    });
  }

  /* ----------------------------------------------------------- modal */

  function openOperation(operation) {
    state.current = operation;

    const category = state.categories.find((c) => c.id === operation.category);
    els.modalTag.textContent = category ? category.name : "";
    els.modalTitle.textContent = operation.name;
    els.modalDesc.textContent = operation.description;

    buildForm(operation);
    hideResult();

    lastFocused = document.activeElement;
    els.modal.hidden = false;
    document.body.style.overflow = "hidden";

    const firstInput = els.fields.querySelector("input, select, textarea");
    if (firstInput) firstInput.focus();
  }

  function closeOperation() {
    els.modal.hidden = true;
    document.body.style.overflow = "";
    state.current = null;

    // devolve o foco ao cartão que abriu o modal (a11y)
    if (lastFocused && document.contains(lastFocused)) {
      lastFocused.focus();
    }
    lastFocused = null;
  }

  function buildForm(operation) {
    els.fields.innerHTML = "";

    operation.fields.forEach((field) => {
      const wrapper = document.createElement("div");
      wrapper.className = "field";

      const label = document.createElement("label");
      label.className = "field-label";
      label.setAttribute("for", `field-${field.name}`);
      label.textContent = field.label;

      if (field.required === false) {
        const optional = document.createElement("span");
        optional.className = "optional";
        optional.textContent = "opcional";
        label.appendChild(optional);
      }

      let control;
      const required = field.required !== false;

      if (field.type === "list" || field.type === "expression") {
        control = document.createElement("textarea");
        control.rows = field.type === "list" ? 2 : 2;
      } else if (field.type === "select") {
        control = document.createElement("select");
        if (required) {
          // Sem uma opção vazia o `required` de um <select> está sempre satisfeito
          const placeholder = document.createElement("option");
          placeholder.value = "";
          placeholder.textContent = "Escolher…";
          control.appendChild(placeholder);
        }
        (field.options || []).forEach((option) => {
          const element = document.createElement("option");
          element.value = option.value;
          element.textContent = option.label;
          control.appendChild(element);
        });
      } else {
        control = document.createElement("input");
        // tipo "text" com inputmode decimal: aceita vírgula (",") como separador
        control.type = "text";
        control.inputMode =
          field.type === "number" || field.type === "integer" ? "decimal" : "text";
      }

      control.id = `field-${field.name}`;
      control.name = field.name;
      control.placeholder = field.placeholder || "";
      control.required = required;
      if (field.hint) {
        control.title = field.hint;
        control.dataset.hint = field.hint;
      }

      control.addEventListener("input", () => clearInvalid(control));
      control.addEventListener("change", () => clearInvalid(control));

      wrapper.append(label, control);

      if (field.hint) {
        const hint = document.createElement("small");
        hint.className = "field-hint";
        hint.textContent = field.hint;
        wrapper.appendChild(hint);
      }

      els.fields.appendChild(wrapper);
    });
  }

  /* -------------------------------------------------------- cálculo */

  async function calculate(event) {
    event.preventDefault();
    if (!state.current) return;

    const inputs = {};
    let firstInvalid = null;

    state.current.fields.forEach((field) => {
      const control = document.getElementById(`field-${field.name}`);
      const value = control ? String(control.value).trim() : "";
      inputs[field.name] = value;

      const message = validateField(field, value);
      if (message) {
        markInvalid(control, message);
        if (!firstInvalid) firstInvalid = { control, message };
      } else {
        clearInvalid(control);
      }
    });

    if (firstInvalid) {
      renderError(firstInvalid.message);
      firstInvalid.control.focus();
      return;
    }

    els.submitBtn.disabled = true;
    els.submitBtn.textContent = "A calcular…";
    showLoading();

    try {
      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: state.current.id, inputs }),
      });

      const data = await response.json();

      if (data.ok) {
        renderResult(data.result);
      } else {
        renderError(data.error || "Não foi possível calcular.");
      }
    } catch (error) {
      console.error(error);
      renderError("Não foi possível ligar ao servidor. Verifica se o backend está a correr.");
    } finally {
      els.submitBtn.disabled = false;
      els.submitBtn.textContent = "Calcular";
    }
  }

  /* -------------------------------------------------- mostrar resultados */

  function showLoading() {
    els.result.hidden = false;
    els.result.innerHTML = `<div class="result-loading">A calcular…</div>`;
  }

  function hideResult() {
    els.result.hidden = true;
    els.result.innerHTML = "";
  }

  function renderError(message) {
    els.result.hidden = false;
    els.result.innerHTML = "";

    const box = document.createElement("div");
    box.className = "result-error";
    box.textContent = message;
    els.result.appendChild(box);
    scrollResultIntoView();
  }

  function renderResult(result) {
    els.result.hidden = false;
    els.result.innerHTML = "";

    const display = document.createElement("div");
    display.className = "result-display";
    display.textContent = result.display;
    els.result.appendChild(display);

    if (Array.isArray(result.details) && result.details.length) {
      const details = document.createElement("div");
      details.className = "result-details";

      result.details.forEach((detail) => {
        const item = document.createElement("div");
        item.className = "detail";

        const label = document.createElement("div");
        label.className = "detail-label";
        label.textContent = detail.label;

        const value = document.createElement("div");
        value.className = "detail-value";
        value.textContent = detail.value;

        item.append(label, value);
        details.appendChild(item);
      });

      els.result.appendChild(details);
    }

    if (Array.isArray(result.steps) && result.steps.length) {
      const steps = document.createElement("ol");
      steps.className = "result-steps";

      result.steps.forEach((step) => {
        const item = document.createElement("li");
        item.textContent = step;
        steps.appendChild(item);
      });

      els.result.appendChild(steps);
    }

    scrollResultIntoView();
  }

  function scrollResultIntoView() {
    els.result.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  /* ------------------------------------------------------ acessibilidade */

  function focusableIn(container) {
    return Array.from(
      container.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), ' +
          "select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])"
      )
    ).filter((element) => element.getClientRects().length > 0);
  }

  // Mantém o Tab dentro do modal enquanto ele estiver aberto
  function trapFocus(event) {
    const focusables = focusableIn(els.modal);
    if (!focusables.length) return;

    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;

    if (event.shiftKey) {
      if (active === first || !els.modal.contains(active)) {
        event.preventDefault();
        last.focus();
      }
    } else if (active === last || !els.modal.contains(active)) {
      event.preventDefault();
      first.focus();
    }
  }

  /* ----------------------------------------------------------- eventos */

  els.form.addEventListener("submit", calculate);

  els.resetBtn.addEventListener("click", () => {
    els.form.reset();
    els.fields
      .querySelectorAll(".invalid")
      .forEach((control) => clearInvalid(control));
    hideResult();
    const firstInput = els.fields.querySelector("input, select, textarea");
    if (firstInput) firstInput.focus();
  });

  els.modalClose.addEventListener("click", closeOperation);

  els.modal.addEventListener("click", (event) => {
    if (event.target === els.modal) closeOperation();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !els.modal.hidden) {
      closeOperation();
      return;
    }
    if (event.key === "Tab" && !els.modal.hidden) {
      trapFocus(event);
      return;
    }
    // Atalho "/" para a pesquisa — apenas quando não se está a escrever
    // num campo (senão quebraria frações como "1/2" ao digitá-las).
    const ativo = document.activeElement;
    const aEscrever =
      ativo &&
      (ativo.tagName === "INPUT" ||
        ativo.tagName === "TEXTAREA" ||
        ativo.tagName === "SELECT" ||
        ativo.isContentEditable);
    if (event.key === "/" && !aEscrever) {
      event.preventDefault();
      els.search.focus();
    }
  });

  let searchTimer = null;
  els.search.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.search = els.search.value;
      renderOperations();
    }, 140);
  });

  init();
})();
