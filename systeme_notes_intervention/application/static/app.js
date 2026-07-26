const months = [
  ["1", "Janvier"],
  ["2", "Février"],
  ["3", "Mars"],
  ["4", "Avril"],
  ["5", "Mai"],
  ["6", "Juin"],
  ["7", "Juillet"],
  ["8", "Août"],
  ["9", "Septembre"],
  ["10", "Octobre"],
  ["11", "Novembre"],
  ["12", "Décembre"],
];

const browserSessionId = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`;
let browserHeartbeatTimer = null;
let browserEventSource = null;
const DISPLAY_STORAGE_KEY = "easyCesuDisplayMode";
const DISPLAY_MANUAL_SCALES = { compact: 0.8, normal: 1, large: 1.1 };
const DISPLAY_MODES = new Set(["auto", ...Object.keys(DISPLAY_MANUAL_SCALES)]);

function automaticDisplayScale() {
  const dpr = Math.max(1, Number(window.devicePixelRatio) || 1);
  const physicalWidth = Math.round((window.screen?.width || window.innerWidth) * dpr);
  const physicalHeight = Math.round((window.screen?.height || window.innerHeight) * dpr);
  if (dpr > 1 && physicalWidth <= 1920 && physicalHeight <= 1200) {
    return Math.max(0.75, Math.min(1, 1 / dpr));
  }
  return 1;
}

function storedDisplayMode() {
  const mode = localStorage.getItem(DISPLAY_STORAGE_KEY);
  return DISPLAY_MODES.has(mode) ? mode : "auto";
}

function applyDisplayMode(requestedMode, { persist = true } = {}) {
  const mode = DISPLAY_MODES.has(requestedMode) ? requestedMode : "auto";
  const scale = DISPLAY_MANUAL_SCALES[mode] || automaticDisplayScale();
  document.documentElement.style.zoom = String(scale);
  window.easyCesuDisplayPreference = { mode, scale };
  if (persist) localStorage.setItem(DISPLAY_STORAGE_KEY, mode);
  if (els.displayModeSelect) els.displayModeSelect.value = mode;
  if (els.displayScaleValue) els.displayScaleValue.value = `${Math.round(scale * 100)} %`;
  return scale;
}

function sendBrowserHeartbeat() {
  fetch("/api/browser-session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: browserSessionId, state: "active" }),
    keepalive: true,
  }).catch(() => {});
}

function startBrowserHeartbeat() {
  // Le flux continu complète le signal de fermeture, parfois perdu quand le navigateur est quitté.
  if (browserHeartbeatTimer) window.clearInterval(browserHeartbeatTimer);
  if (browserEventSource) browserEventSource.close();
  browserEventSource = new EventSource(`/api/browser-events?session_id=${encodeURIComponent(browserSessionId)}`);
  sendBrowserHeartbeat();
  browserHeartbeatTimer = window.setInterval(sendBrowserHeartbeat, 10000);
}

function closeBrowserSession() {
  // sendBeacon a le temps d'envoyer ce message pendant la fermeture de l'onglet.
  if (browserHeartbeatTimer) window.clearInterval(browserHeartbeatTimer);
  if (browserEventSource) browserEventSource.close();
  browserHeartbeatTimer = null;
  browserEventSource = null;
  const payload = JSON.stringify({ session_id: browserSessionId, state: "closed" });
  navigator.sendBeacon("/api/browser-session", payload);
}

window.addEventListener("pageshow", startBrowserHeartbeat);
window.addEventListener("pagehide", closeBrowserSession);

const state = {
  clients: [],
  interventions: [],
  annualOverview: null,
  overview: null,
  overviewYear: null,
  reminders: { late: [], today_items: [], upcoming: [], notifications: [], items: [] },
  selectedClientName: "",
  clientReminders: [],
  defaultRate: 22,
  notesDir: "",
  dataDir: "",
  exportDir: "",
  databasePath: "",
  sourceDir: "",
  clientsFile: "",
  sourcePattern: "Suivi de paye {year}.xlsx",
  profiles: [],
  activeProfileId: "",
  creatingProfile: false,
  initialSetupRequired: false,
  setupContext: "first-run",
  setupStep: 1,
  categories: [],
  notes: [],
  payments: [],
  documentTemplates: [],
  selectedTemplateId: null,
  templateDraft: null,
  templateDirty: false,
  community: null,
};

const els = {
  faviconLink: document.querySelector("#faviconLink"),
  statusLine: document.querySelector("#statusLine"),
  appVersion: document.querySelector("#appVersion"),
  footerVersion: document.querySelector("#footerVersion"),
  footerGithubBtn: document.querySelector("#footerGithubBtn"),
  yearFilter: document.querySelector("#yearFilter"),
  monthFilter: document.querySelector("#monthFilter"),
  generateBtn: document.querySelector("#generateBtn"),
  exportBtn: document.querySelector("#exportBtn"),
  clientsTopBtn: document.querySelector("#clientsTopBtn"),
  displayModeSelect: document.querySelector("#displayModeSelect"),
  displayScaleValue: document.querySelector("#displayScaleValue"),
  form: document.querySelector("#interventionForm"),
  editingId: document.querySelector("#editingId"),
  formTitle: document.querySelector("#formTitle"),
  dateInput: document.querySelector("#dateInput"),
  clientInput: document.querySelector("#clientInput"),
  clientsList: document.querySelector("#clientsList"),
  durationInput: document.querySelector("#durationInput"),
  rateInput: document.querySelector("#rateInput"),
  locationInput: document.querySelector("#locationInput"),
  taskInput: document.querySelector("#taskInput"),
  statusInput: document.querySelector("#statusInput"),
  plannedStartInput: document.querySelector("#plannedStartInput"),
  plannedEndInput: document.querySelector("#plannedEndInput"),
  actualStartInput: document.querySelector("#actualStartInput"),
  actualEndInput: document.querySelector("#actualEndInput"),
  breakInput: document.querySelector("#breakInput"),
  travelInput: document.querySelector("#travelInput"),
  plannedAmountInput: document.querySelector("#plannedAmountInput"),
  receivedAmountInput: document.querySelector("#receivedAmountInput"),
  transmittedInput: document.querySelector("#transmittedInput"),
  paidInput: document.querySelector("#paidInput"),
  resetBtn: document.querySelector("#resetBtn"),
  saveBtn: document.querySelector("#saveBtn"),
  tabs: document.querySelectorAll("[data-view]"),
  viewPanels: document.querySelectorAll("[data-view-panel]"),
  metricInterventions: document.querySelector("#metricInterventions"),
  metricClients: document.querySelector("#metricClients"),
  metricHours: document.querySelector("#metricHours"),
  metricNet: document.querySelector("#metricNet"),
  quickProfileSelect: document.querySelector("#quickProfileSelect"),
  profileSelect: document.querySelector("#profileSelect"),
  newProfileBtn: document.querySelector("#newProfileBtn"),
  cancelNewProfileBtn: document.querySelector("#cancelNewProfileBtn"),
  profileLabelInput: document.querySelector("#profileLabelInput"),
  employeeNameInput: document.querySelector("#employeeNameInput"),
  employeeAddressInput: document.querySelector("#employeeAddressInput"),
  employeePhoneInput: document.querySelector("#employeePhoneInput"),
  employeeEmailInput: document.querySelector("#employeeEmailInput"),
  employeeSsInput: document.querySelector("#employeeSsInput"),
  employeeBirthInput: document.querySelector("#employeeBirthInput"),
  primaryActivityInput: document.querySelector("#primaryActivityInput"),
  shortcutIconInput: document.querySelector("#shortcutIconInput"),
  commercialNameInput: document.querySelector("#commercialNameInput"),
  backupDirInput: document.querySelector("#backupDirInput"),
  defaultRateInput: document.querySelector("#defaultRateInput"),
  sourceDirInput: document.querySelector("#sourceDirInput"),
  browseSourceDirBtn: document.querySelector("#browseSourceDirBtn"),
  sourcePatternInput: document.querySelector("#sourcePatternInput"),
  clientsFileInput: document.querySelector("#clientsFileInput"),
  browseClientsFileBtn: document.querySelector("#browseClientsFileBtn"),
  setupFoldersBtn: document.querySelector("#setupFoldersBtn"),
  dataDirInput: document.querySelector("#dataDirInput"),
  browseDataDirBtn: document.querySelector("#browseDataDirBtn"),
  databaseProfileName: document.querySelector("#databaseProfileName"),
  databasePathInput: document.querySelector("#databasePathInput"),
  selectDatabaseFileBtn: document.querySelector("#selectDatabaseFileBtn"),
  importDatabaseBtn: document.querySelector("#importDatabaseBtn"),
  backupDatabaseBtn: document.querySelector("#backupDatabaseBtn"),
  planningLate: document.querySelector("#planningLate"),
  planningToday: document.querySelector("#planningToday"),
  planningUpcoming: document.querySelector("#planningUpcoming"),
  planningTodayBtn: document.querySelector("#planningTodayBtn"),
  overviewPanel: document.querySelector("#overviewPanel"),
  annualTitle: document.querySelector("#annualTitle"),
  annualSubtitle: document.querySelector("#annualSubtitle"),
  annualGranularity: document.querySelector("#annualGranularity"),
  annualNetChart: document.querySelector("#annualNetChart"),
  annualHoursChart: document.querySelector("#annualHoursChart"),
  annualInsight: document.querySelector("#annualInsight"),
  annualNetChartTitle: document.querySelector("#annualNetChartTitle"),
  annualHoursChartTitle: document.querySelector("#annualHoursChartTitle"),
  comparisonDetails: document.querySelector(".comparison-details"),
  overviewHours: document.querySelector("#overviewHours"),
  overviewNet: document.querySelector("#overviewNet"),
  overviewInterventions: document.querySelector("#overviewInterventions"),
  overviewAverage: document.querySelector("#overviewAverage"),
  overviewAverageLabel: document.querySelector("#overviewAverageLabel"),
  overviewBusiest: document.querySelector("#overviewBusiest"),
  overviewDetail: document.querySelector("#overviewDetail"),
  overviewGranularity: document.querySelector("#overviewGranularity"),
  overviewStart: document.querySelector("#overviewStart"),
  overviewEnd: document.querySelector("#overviewEnd"),
  overviewReference: document.querySelector("#overviewReference"),
  overviewApplyBtn: document.querySelector("#overviewApplyBtn"),
  overviewHoursVariation: document.querySelector("#overviewHoursVariation"),
  overviewHoursReference: document.querySelector("#overviewHoursReference"),
  overviewNetVariation: document.querySelector("#overviewNetVariation"),
  overviewNetReference: document.querySelector("#overviewNetReference"),
  overviewInterventionsVariation: document.querySelector("#overviewInterventionsVariation"),
  overviewInterventionsReference: document.querySelector("#overviewInterventionsReference"),
  netChart: document.querySelector("#netChart"),
  netChartScale: document.querySelector("#netChartScale"),
  hoursChart: document.querySelector("#hoursChart"),
  hoursChartScale: document.querySelector("#hoursChartScale"),
  overviewBody: document.querySelector("#overviewBody"),
  setupAssistantDialog: document.querySelector("#setupAssistantDialog"),
  setupIcon: document.querySelector("#setupIcon"),
  setupAssistantTitle: document.querySelector("#setupAssistantTitle"),
  setupAssistantText: document.querySelector("#setupAssistantText"),
  setupAssistantStartBtn: document.querySelector("#setupAssistantStartBtn"),
  setupAssistantLaterBtn: document.querySelector("#setupAssistantLaterBtn"),
  notesDirInput: document.querySelector("#notesDirInput"),
  browseNotesDirBtn: document.querySelector("#browseNotesDirBtn"),
  exportDirInput: document.querySelector("#exportDirInput"),
  browseExportDirBtn: document.querySelector("#browseExportDirBtn"),
  deleteProfileBtn: document.querySelector("#deleteProfileBtn"),
  saveSettingsBtn: document.querySelector("#saveSettingsBtn"),
  githubSourceBtn: document.querySelector("#githubSourceBtn"),
  githubStarBtn: document.querySelector("#githubStarBtn"),
  githubIssueBtn: document.querySelector("#githubIssueBtn"),
  paypalSupportBtn: document.querySelector("#paypalSupportBtn"),
  supportDialog: document.querySelector("#supportDialog"),
  supportDialogPayPalBtn: document.querySelector("#supportDialogPayPalBtn"),
  supportDialogCloseBtn: document.querySelector("#supportDialogCloseBtn"),
  supportDialogCloseIconBtn: document.querySelector("#supportDialogCloseIconBtn"),
  supportReminderEnabledInput: document.querySelector("#supportReminderEnabledInput"),
  supportReminder: document.querySelector("#supportReminder"),
  supportReminderOpenBtn: document.querySelector("#supportReminderOpenBtn"),
  supportReminderDismissBtn: document.querySelector("#supportReminderDismissBtn"),
  supportReminderDisableBtn: document.querySelector("#supportReminderDisableBtn"),
  monthTitle: document.querySelector("#monthTitle"),
  searchInput: document.querySelector("#searchInput"),
  clientsShortcutBtn: document.querySelector("#clientsShortcutBtn"),
  refreshClientsBtn: document.querySelector("#refreshClientsBtn"),
  interventionsBody: document.querySelector("#interventionsBody"),
  clientsPanel: document.querySelector("#clientsPanel"),
  clientForm: document.querySelector("#clientForm"),
  clientOriginalName: document.querySelector("#clientOriginalName"),
  clientNameInput: document.querySelector("#clientNameInput"),
  clientEmailInput: document.querySelector("#clientEmailInput"),
  clientCesuInput: document.querySelector("#clientCesuInput"),
  clientRateInput: document.querySelector("#clientRateInput"),
  clientPhoneInput: document.querySelector("#clientPhoneInput"),
  clientAddressInput: document.querySelector("#clientAddressInput"),
  clientResetBtn: document.querySelector("#clientResetBtn"),
  clientSaveBtn: document.querySelector("#clientSaveBtn"),
  clientSearchInput: document.querySelector("#clientSearchInput"),
  clientsBody: document.querySelector("#clientsBody"),
  reminderForm: document.querySelector("#reminderForm"),
  reminderId: document.querySelector("#reminderId"),
  reminderTitleInput: document.querySelector("#reminderTitleInput"),
  reminderDateInput: document.querySelector("#reminderDateInput"),
  reminderTimeInput: document.querySelector("#reminderTimeInput"),
  reminderRecurrenceInput: document.querySelector("#reminderRecurrenceInput"),
  reminderIntervalInput: document.querySelector("#reminderIntervalInput"),
  reminderAnticipationInput: document.querySelector("#reminderAnticipationInput"),
  reminderUnitInput: document.querySelector("#reminderUnitInput"),
  reminderDescriptionInput: document.querySelector("#reminderDescriptionInput"),
  reminderActiveInput: document.querySelector("#reminderActiveInput"),
  reminderResetBtn: document.querySelector("#reminderResetBtn"),
  reminderSaveBtn: document.querySelector("#reminderSaveBtn"),
  reminderClientHint: document.querySelector("#reminderClientHint"),
  clientReminders: document.querySelector("#clientReminders"),
  toast: document.querySelector("#toast"),
  setupAssistantChoice: document.querySelector("#setupAssistantChoice"),
  setupAssistantEmptyBtn: document.querySelector("#setupAssistantEmptyBtn"),
  setupAssistantRestoreBtn: document.querySelector("#setupAssistantRestoreBtn"),
  setupAssistantProgress: document.querySelector("#setupAssistantProgress"),
  setupSteps: document.querySelectorAll("[data-setup-step]"),
  setupNameInput: document.querySelector("#setupNameInput"),
  setupPhoneInput: document.querySelector("#setupPhoneInput"),
  setupActivityInput: document.querySelector("#setupActivityInput"),
  setupAssistantPreviousBtn: document.querySelector("#setupAssistantPreviousBtn"),
  setupAssistantNextBtn: document.querySelector("#setupAssistantNextBtn"),
  followupPanel: document.querySelector("#followupPanel"),
  noteForm: document.querySelector("#noteForm"),
  noteClientInput: document.querySelector("#noteClientInput"),
  noteCategoryInput: document.querySelector("#noteCategoryInput"),
  notePriorityInput: document.querySelector("#notePriorityInput"),
  noteBodyInput: document.querySelector("#noteBodyInput"),
  noteCarryInput: document.querySelector("#noteCarryInput"),
  notesList: document.querySelector("#notesList"),
  paymentForm: document.querySelector("#paymentForm"),
  paymentClientInput: document.querySelector("#paymentClientInput"),
  paymentAmountInput: document.querySelector("#paymentAmountInput"),
  paymentDateInput: document.querySelector("#paymentDateInput"),
  paymentMethodInput: document.querySelector("#paymentMethodInput"),
  paymentsList: document.querySelector("#paymentsList"),
  templatesPanel: document.querySelector("#templatesPanel"),
  templateSelect: document.querySelector("#templateSelect"),
  templateNewBtn: document.querySelector("#templateNewBtn"),
  templateDuplicateBtn: document.querySelector("#templateDuplicateBtn"),
  templateDeleteBtn: document.querySelector("#templateDeleteBtn"),
  templateImportBtn: document.querySelector("#templateImportBtn"),
  templateNameInput: document.querySelector("#templateNameInput"),
  templateDefaultInput: document.querySelector("#templateDefaultInput"),
  templateBlocks: document.querySelector("#templateBlocks"),
  templateLabelInputs: document.querySelectorAll("[data-template-label]"),
  templateBodySizeInput: document.querySelector("#templateBodySizeInput"),
  templateTitleSizeInput: document.querySelector("#templateTitleSizeInput"),
  templateTableSizeInput: document.querySelector("#templateTableSizeInput"),
  templateTextColorInput: document.querySelector("#templateTextColorInput"),
  templateTitleColorInput: document.querySelector("#templateTitleColorInput"),
  templateHeaderColorInput: document.querySelector("#templateHeaderColorInput"),
  templateTotalColorInput: document.querySelector("#templateTotalColorInput"),
  templateBorderColorInput: document.querySelector("#templateBorderColorInput"),
  templateMarginTopInput: document.querySelector("#templateMarginTopInput"),
  templateMarginBottomInput: document.querySelector("#templateMarginBottomInput"),
  templateMarginLeftInput: document.querySelector("#templateMarginLeftInput"),
  templateMarginRightInput: document.querySelector("#templateMarginRightInput"),
  templateIdentityGapInput: document.querySelector("#templateIdentityGapInput"),
  templateTitleGapInput: document.querySelector("#templateTitleGapInput"),
  templateRowHeightInput: document.querySelector("#templateRowHeightInput"),
  templateMinimumRowsInput: document.querySelector("#templateMinimumRowsInput"),
  templateResetBtn: document.querySelector("#templateResetBtn"),
  templateSaveBtn: document.querySelector("#templateSaveBtn"),
  templateTestPdfBtn: document.querySelector("#templateTestPdfBtn"),
  templateExportBtn: document.querySelector("#templateExportBtn"),
  templatePaper: document.querySelector("#templatePaper"),
  templateUnsavedBadge: document.querySelector("#templateUnsavedBadge"),
};

function euro(value) {
  return new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(Number(value || 0));
}

function dateFr(value) {
  return new Intl.DateTimeFormat("fr-FR").format(new Date(`${value}T00:00:00`));
}

function parseDurationInput(value) {
  const raw = String(value ?? "").trim().toLowerCase().replace(",", ".");
  const timeMatch = raw.match(/^(\d+)\s*[:h]\s*(\d{1,2})$/);
  if (timeMatch) {
    const hours = Number(timeMatch[1]);
    const minutes = Number(timeMatch[2]);
    return minutes < 60 ? hours + minutes / 60 : Number.NaN;
  }
  const decimal = Number(raw);
  return Number.isFinite(decimal) ? decimal : Number.NaN;
}

function formatDurationInput(value) {
  const hours = typeof value === "string" ? parseDurationInput(value) : Number(value);
  if (!Number.isFinite(hours) || hours < 0) return "";
  const totalMinutes = Math.round(hours * 60);
  return `${Math.floor(totalMinutes / 60)}:${String(totalMinutes % 60).padStart(2, "0")}`;
}

function durationLabel(hours) {
  return formatDurationInput(Number(hours || 0));
}

function adjustSteppedNumber(input, direction) {
  // Les gros boutons ont volontairement un pas simple : 30 minutes ou 0,50 euro.
  const step = 0.5;
  const current = input === els.durationInput
    ? parseDurationInput(input.value)
    : Number.parseFloat(input.value);
  const startingValue = Number.isFinite(current) ? current : 0;
  let nextValue = Math.round((startingValue + direction * step) * 100) / 100;
  const minimum = Number.parseFloat(input.dataset.min || input.min);
  const maximum = Number.parseFloat(input.dataset.max || input.max);
  if (Number.isFinite(minimum)) nextValue = Math.max(minimum, nextValue);
  if (Number.isFinite(maximum)) nextValue = Math.min(maximum, nextValue);

  input.value = input === els.durationInput
    ? formatDurationInput(nextValue)
    : nextValue.toFixed(2);
  input.dispatchEvent(new Event("input", { bubbles: true }));
  input.dispatchEvent(new Event("change", { bubbles: true }));
}

function rateLabel(value) {
  const rate = Number(value || 0);
  return rate > 0 ? `${euro(rate)} / h` : `Défaut (${euro(state.defaultRate)} / h)`;
}

function currentProfile() {
  return state.profiles.find((profile) => profile.id === state.activeProfileId) || state.profiles[0] || null;
}

function applyProfileIcon(iconKey) {
  const supported = new Set([
    "generique",
    "jardinage",
    "bricolage",
    "menage",
    "aide_a_domicile",
    "garde_d_enfants",
    "soutien_scolaire",
    "accompagnement",
    "assistance_administrative",
    "informatique",
  ]);
  const key = supported.has(iconKey) ? iconKey : "generique";
  const path = `/icons/${key}.png?v=20260724-v210b`;
  els.faviconLink.href = path;
  els.setupIcon.src = path;
}

function renderProfiles() {
  const options = state.profiles
    .map((profile) => `<option value="${escapeHtml(profile.id)}">${escapeHtml(profile.label || profile.name || profile.id)}</option>`)
    .join("");
  els.quickProfileSelect.innerHTML = options;
  els.quickProfileSelect.value = state.activeProfileId;
  els.profileSelect.innerHTML = state.creatingProfile
    ? `<option value="__new">Nouveau compte</option>${options}`
    : options;
  els.profileSelect.value = state.creatingProfile ? "__new" : state.activeProfileId;
}

function setProfileForm(profile = {}) {
  els.databaseProfileName.textContent = profile.label || profile.name || "Compte actif";
  els.profileLabelInput.value = profile.label || "";
  els.employeeNameInput.value = profile.name || "";
  els.employeeAddressInput.value = profile.address || "";
  els.employeePhoneInput.value = profile.phone || "";
  els.employeeEmailInput.value = profile.email || "";
  els.employeeSsInput.value = profile.ss_number || "";
  els.employeeBirthInput.value = profile.birth_info || "";
  els.primaryActivityInput.value = profile.primary_activity || "autre";
  els.shortcutIconInput.value = profile.shortcut_icon || profile.primary_activity || "generique";
  if (!els.shortcutIconInput.value) els.shortcutIconInput.value = "generique";
  applyProfileIcon(els.shortcutIconInput.value);
  els.commercialNameInput.value = profile.commercial_name || "";
  els.backupDirInput.value = profile.backup_dir || "";
  const rate = Number(profile.default_hourly_rate || state.defaultRate || 22);
  state.defaultRate = rate;
  els.defaultRateInput.value = rate.toFixed(2);
  state.sourceDir = "suivi_paye_dir" in profile ? profile.suivi_paye_dir || "" : state.sourceDir || "";
  els.sourceDirInput.value = state.sourceDir;
  state.sourcePattern = profile.suivi_paye_pattern || state.sourcePattern || "Suivi de paye {year}.xlsx";
  els.sourcePatternInput.value = state.sourcePattern;
  state.clientsFile = "fichier_clients" in profile ? profile.fichier_clients || "" : state.clientsFile || "";
  els.clientsFileInput.value = state.clientsFile;
  state.dataDir = "data_dir" in profile ? profile.data_dir || "" : state.dataDir || "";
  els.dataDirInput.value = state.dataDir;
  state.databasePath = "database_path" in profile ? profile.database_path || "" : state.databasePath || "";
  els.databasePathInput.value = state.databasePath;
  state.notesDir = "notes_intervention_dir" in profile ? profile.notes_intervention_dir || "" : state.notesDir || "";
  els.notesDirInput.value = state.notesDir;
  state.exportDir = "export_dir" in profile ? profile.export_dir || "" : state.exportDir || "";
  els.exportDirInput.value = state.exportDir;
}

function setProfileEditorMode(creating) {
  state.creatingProfile = creating;
  els.cancelNewProfileBtn.hidden = !creating;
  els.deleteProfileBtn.hidden = creating;
  els.deleteProfileBtn.disabled = creating || state.profiles.length <= 1;
  els.saveSettingsBtn.textContent = creating ? "Créer le compte" : "Enregistrer les réglages";
  renderProfiles();
}

function profilePayload() {
  return {
    label: els.profileLabelInput.value.trim(),
    name: els.employeeNameInput.value.trim(),
    address: els.employeeAddressInput.value.trim(),
    phone: els.employeePhoneInput.value.trim(),
    email: els.employeeEmailInput.value.trim(),
    ss_number: els.employeeSsInput.value.trim(),
    birth_info: els.employeeBirthInput.value.trim(),
    primary_activity: els.primaryActivityInput.value,
    shortcut_icon: els.shortcutIconInput.value,
    commercial_name: els.commercialNameInput.value.trim(),
    backup_dir: els.backupDirInput.value.trim(),
    default_hourly_rate: Number(els.defaultRateInput.value),
    suivi_paye_dir: els.sourceDirInput.value.trim(),
    suivi_paye_pattern: els.sourcePatternInput.value.trim(),
    fichier_clients: els.clientsFileInput.value.trim(),
    data_dir: els.dataDirInput.value.trim(),
    notes_intervention_dir: els.notesDirInput.value.trim(),
    export_dir: els.exportDirInput.value.trim(),
  };
}

function applySettings(settings = {}) {
  state.defaultRate = Number(settings.default_hourly_rate || state.defaultRate || 22);
  state.sourceDir = settings.profile?.suivi_paye_dir || state.sourceDir || "";
  state.sourcePattern = settings.profile?.suivi_paye_pattern || state.sourcePattern || "Suivi de paye {year}.xlsx";
  state.clientsFile = settings.profile?.fichier_clients || state.clientsFile || "";
  state.dataDir = settings.data_dir || state.dataDir || "";
  state.databasePath = settings.profile?.database_path || state.databasePath || "";
  state.notesDir = settings.notes_intervention_dir || state.notesDir || "";
  state.exportDir = settings.export_dir || state.exportDir || "";
  state.profiles = settings.profiles || state.profiles;
  state.activeProfileId = settings.active_profile_id || settings.profile?.id || state.activeProfileId;
  state.initialSetupRequired = Boolean(settings.initial_setup_required);
  setProfileEditorMode(false);
  setProfileForm(settings.profile || currentProfile() || {});
}

function showSetupAssistant(context = "first-run") {
  const messages = {
    "first-run": {
      title: "Bienvenue dans Easy CESU",
      text: "Choisis où ranger les fichiers de ton premier compte.",
    },
    import: {
      title: "Base importée",
      text: "Choisis maintenant où ranger cette base, les notes et les exports.",
    },
    account: {
      title: "Nouveau compte créé",
      text: "Choisis où ranger la base et les documents de ce nouveau compte.",
    },
    database: {
      title: "Base sélectionnée",
      text: "Choisis où ranger la base et les documents associés à ce compte.",
    },
  };
  const message = messages[context] || messages["first-run"];
  state.setupContext = context;
  state.setupStep = context === "first-run" ? 1 : 4;
  els.setupAssistantChoice.hidden = context !== "first-run";
  els.setupAssistantTitle.textContent = message.title;
  els.setupAssistantText.textContent = message.text;
  const profile = currentProfile() || {};
  els.setupNameInput.value = profile.name || "";
  els.setupPhoneInput.value = profile.phone || "";
  els.setupActivityInput.value = profile.primary_activity || "autre";
  renderSetupStep();
  if (!els.setupAssistantDialog.open) {
    els.setupAssistantDialog.showModal();
  }
}

function renderSetupStep() {
  els.setupSteps.forEach((step) => { step.hidden = Number(step.dataset.setupStep) !== state.setupStep; });
  els.setupAssistantProgress.textContent = `Étape ${state.setupStep} sur 5`;
  els.setupAssistantPreviousBtn.hidden = state.setupStep <= 1;
  els.setupAssistantNextBtn.hidden = state.setupStep >= 5 || state.setupStep === 4;
  els.setupAssistantStartBtn.hidden = state.setupStep !== 4;
  els.setupAssistantStartBtn.textContent = "Choisir le dossier principal";
  if (state.setupStep === 5) {
    els.setupAssistantNextBtn.hidden = false;
    els.setupAssistantNextBtn.textContent = "Terminer";
  } else {
    els.setupAssistantNextBtn.textContent = "Suivant";
  }
}

async function advanceSetupAssistant() {
  if (state.setupStep === 1) {
    state.setupStep = 2;
  } else if (state.setupStep === 2) {
    const profile = currentProfile();
    await api(`/api/profiles/${encodeURIComponent(profile.id)}`, { method: "PUT", body: JSON.stringify({ name: els.setupNameInput.value.trim(), phone: els.setupPhoneInput.value.trim() }) });
    state.setupStep = 3;
  } else if (state.setupStep === 3) {
    const profile = currentProfile();
    const activity = els.setupActivityInput.value;
    const shortcutIcon = activity === "autre" ? "generique" : activity;
    const payload = await api(`/api/profiles/${encodeURIComponent(profile.id)}`, {
      method: "PUT",
      body: JSON.stringify({ primary_activity: activity, shortcut_icon: shortcutIcon }),
    });
    if (payload.settings) applySettings(payload.settings);
    state.setupStep = 4;
  } else if (state.setupStep === 5) {
    hideSetupAssistant();
    showToast("Configuration terminée.");
    return;
  }
  renderSetupStep();
}

function hideSetupAssistant() {
  if (els.setupAssistantDialog.open) {
    els.setupAssistantDialog.close();
  }
}

function applyBootstrap(bootstrap, options = {}) {
  state.clients = bootstrap.clients || state.clients;
  state.reminders = bootstrap.reminders || state.reminders;
  applySettings(bootstrap.settings || {});
  if (!options.keepFilters) {
    els.yearFilter.value = bootstrap.year;
    els.monthFilter.value = bootstrap.month;
  }
  renderClients();
  resetForm();
  resetClientForm();
  renderPlanning();
  if (bootstrap.today) {
    els.dateInput.value = bootstrap.today;
  }
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => els.toast.classList.remove("visible"), 5200);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Erreur inconnue");
  }
  return payload;
}

function applyCommunity(payload) {
  state.community = payload;
  const reminder = payload?.support_reminder || {};
  els.supportReminderEnabledInput.checked = Boolean(reminder.enabled);
  els.supportReminder.hidden = !reminder.due;
}

async function loadCommunity() {
  applyCommunity(await api("/api/community"));
}

async function openExternal(linkId) {
  const result = await api("/api/open-external", {
    method: "POST",
    body: JSON.stringify({ link_id: linkId }),
  });
  showToast(result.opened ? "Ouverture dans le navigateur." : "Le navigateur n’a pas pu être ouvert.");
}

async function updateSupportReminder(action) {
  const payload = await api("/api/support-reminder", {
    method: "POST",
    body: JSON.stringify({ action }),
  });
  applyCommunity({ ...(state.community || {}), support_reminder: payload.support_reminder });
}

async function openSupportFromReminder() {
  await updateSupportReminder("dismiss");
  showSupportDialog();
}

function showSupportDialog() {
  if (typeof els.supportDialog.showModal === "function") {
    els.supportDialog.showModal();
  } else {
    els.supportDialog.setAttribute("open", "");
  }
}

function closeSupportDialog() {
  if (typeof els.supportDialog.close === "function") {
    els.supportDialog.close();
  } else {
    els.supportDialog.removeAttribute("open");
  }
}

function selectedYear() {
  return Number(els.yearFilter.value);
}

function selectedMonth() {
  return Number(els.monthFilter.value);
}

function selectedMonthName() {
  return months.find(([value]) => Number(value) === selectedMonth())?.[1] || "";
}

function fillMonthSelect() {
  els.monthFilter.innerHTML = months.map(([value, label]) => `<option value="${value}">${label}</option>`).join("");
}

function renderClients() {
  els.clientsList.innerHTML = state.clients
    .map((client) => `<option value="${escapeHtml(client.name)}"></option>`)
    .join("");
  renderClientsTable();
  const clientOptions = `<option value="">Choisir un client</option>${state.clients.map((client) => `<option value="${escapeHtml(client.name)}">${escapeHtml(client.name)}</option>`).join("")}`;
  if (els.noteClientInput) els.noteClientInput.innerHTML = clientOptions;
  if (els.paymentClientInput) els.paymentClientInput.innerHTML = clientOptions;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderClientsTable() {
  const term = els.clientSearchInput.value.trim().toLowerCase();
  const rows = state.clients.filter((client) => {
    const haystack = `${client.name} ${client.email} ${client.cesu} ${client.hourly_rate} ${client.phone} ${client.address}`.toLowerCase();
    return !term || haystack.includes(term);
  });
  if (!rows.length) {
    els.clientsBody.innerHTML = `<tr><td class="empty-row" colspan="7">Aucun client</td></tr>`;
    return;
  }
  els.clientsBody.innerHTML = rows
    .map((client) => {
      const email = client.email
        ? `<a href="mailto:${escapeHtml(client.email)}">${escapeHtml(client.email)}</a>`
        : "";
      return `
      <tr>
        <td>${escapeHtml(client.name)}</td>
        <td>${email}</td>
        <td>${escapeHtml(client.cesu || "")}</td>
        <td>${rateLabel(client.hourly_rate)}</td>
        <td>${escapeHtml(client.phone || "")}</td>
        <td>${escapeHtml(client.address || "")}</td>
        <td>
          <div class="row-actions">
            <button class="icon-btn" title="Modifier" data-edit-client="${escapeHtml(client.name)}">✎</button>
            <button class="icon-btn delete-btn" title="Supprimer" data-delete-client="${escapeHtml(client.name)}">×</button>
          </div>
        </td>
      </tr>`;
    })
    .join("");
}

const templateBlockLabels = {
  identity: "Identité et employeur",
  title: "Titre de la note",
  table: "Tableau des interventions",
};

function cloneData(value) {
  return JSON.parse(JSON.stringify(value));
}

function currentDocumentTemplate() {
  return state.documentTemplates.find((item) => Number(item.id) === Number(state.selectedTemplateId)) || null;
}

function setTemplateDirty(dirty) {
  state.templateDirty = Boolean(dirty);
  els.templateUnsavedBadge.hidden = !state.templateDirty;
}

function clearDocumentTemplateState() {
  state.documentTemplates = [];
  state.selectedTemplateId = null;
  state.templateDraft = null;
  setTemplateDirty(false);
  els.templateSelect.innerHTML = "";
  els.templateBlocks.innerHTML = "";
  els.templatePaper.innerHTML = "";
}

function safeTemplateNumber(input, fallback) {
  const value = Number(input.value);
  return Number.isFinite(value) ? value : fallback;
}

function syncTemplateDraftFromForm(markDirty = true) {
  if (!state.templateDraft) return;
  const draft = state.templateDraft;
  const configuration = draft.configuration;
  draft.name = els.templateNameInput.value.trim();
  draft.is_default = els.templateDefaultInput.checked;
  els.templateLabelInputs.forEach((input) => {
    configuration.labels[input.dataset.templateLabel] = input.value;
  });
  configuration.typography.body_size = safeTemplateNumber(els.templateBodySizeInput, configuration.typography.body_size);
  configuration.typography.title_size = safeTemplateNumber(els.templateTitleSizeInput, configuration.typography.title_size);
  configuration.typography.table_size = safeTemplateNumber(els.templateTableSizeInput, configuration.typography.table_size);
  configuration.typography.text_color = els.templateTextColorInput.value;
  configuration.typography.title_color = els.templateTitleColorInput.value;
  configuration.table.header_background = els.templateHeaderColorInput.value;
  configuration.table.total_background = els.templateTotalColorInput.value;
  configuration.table.border_color = els.templateBorderColorInput.value;
  configuration.page.top_margin_cm = safeTemplateNumber(els.templateMarginTopInput, configuration.page.top_margin_cm);
  configuration.page.bottom_margin_cm = safeTemplateNumber(els.templateMarginBottomInput, configuration.page.bottom_margin_cm);
  configuration.page.left_margin_cm = safeTemplateNumber(els.templateMarginLeftInput, configuration.page.left_margin_cm);
  configuration.page.right_margin_cm = safeTemplateNumber(els.templateMarginRightInput, configuration.page.right_margin_cm);
  configuration.spacing.identity_after_cm = safeTemplateNumber(els.templateIdentityGapInput, configuration.spacing.identity_after_cm);
  configuration.spacing.title_after_cm = safeTemplateNumber(els.templateTitleGapInput, configuration.spacing.title_after_cm);
  configuration.table.row_height_cm = safeTemplateNumber(els.templateRowHeightInput, configuration.table.row_height_cm);
  configuration.table.minimum_rows = Math.round(safeTemplateNumber(els.templateMinimumRowsInput, configuration.table.minimum_rows));
  if (markDirty) setTemplateDirty(true);
  renderTemplatePreview();
}

function renderTemplateSelector() {
  els.templateSelect.innerHTML = state.documentTemplates
    .map((item) => `<option value="${item.id}">${escapeHtml(item.name)}${item.is_default ? " · utilisé" : ""}</option>`)
    .join("");
  els.templateSelect.value = String(state.selectedTemplateId || "");
}

function renderTemplateBlocks() {
  if (!state.templateDraft) {
    els.templateBlocks.innerHTML = "";
    return;
  }
  const configuration = state.templateDraft.configuration;
  els.templateBlocks.innerHTML = configuration.blocks.map((block, index) => `
    <div class="template-block-row">
      <label>
        <input type="checkbox" data-template-visible="${block}" ${configuration.visible[block] ? "checked" : ""} ${block === "table" ? "disabled" : ""} />
        <span>${escapeHtml(templateBlockLabels[block] || block)}</span>
      </label>
      <button class="icon-btn" type="button" title="Monter" aria-label="Monter" data-template-move="${block}" data-template-direction="-1" ${index === 0 ? "disabled" : ""}>↑</button>
      <button class="icon-btn" type="button" title="Descendre" aria-label="Descendre" data-template-move="${block}" data-template-direction="1" ${index === configuration.blocks.length - 1 ? "disabled" : ""}>↓</button>
    </div>
  `).join("");
}

function renderTemplatePreview() {
  if (!state.templateDraft) {
    els.templatePaper.innerHTML = "";
    return;
  }
  const configuration = state.templateDraft.configuration;
  const labels = configuration.labels;
  const profile = currentProfile() || {};
  const employeeLines = [
    profile.name || "Marie Dupont",
    ...(profile.address || "10 rue des Lilas\n49000 Angers").split(/\r?\n/),
    profile.phone || "06 00 00 00 00",
    profile.email || "contact@exemple.fr",
  ].filter(Boolean);
  const employeeHtml = employeeLines
    .map((line, index) => index === 0 ? `<strong>${escapeHtml(line)}</strong>` : escapeHtml(line))
    .join("<br>");

  const identity = `
    <div class="template-preview-identity">
      <div class="template-preview-employee">${employeeHtml}</div>
      <div class="template-preview-employer">
        <strong>${escapeHtml(labels.employer)}</strong><span>Client exemple</span>
        <strong>${escapeHtml(labels.month)}</strong><span>Juillet 2026</span>
      </div>
    </div>`;
  const title = `<div class="template-preview-title">${escapeHtml(labels.title)}</div>`;
  const minimumRows = Math.max(2, Math.min(24, Number(configuration.table.minimum_rows || 15)));
  const sampleRows = [
    ["03/07/26", "22,00 €", "2:00", "44,00 €"],
    ["10/07/26", "22,00 €", "1:30", "33,00 €"],
  ];
  while (sampleRows.length < minimumRows) sampleRows.push(["", "", "", ""]);
  const rowsHtml = sampleRows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("");
  const table = `
    <table class="template-preview-table">
      <thead><tr><th>${escapeHtml(labels.date)}</th><th>${escapeHtml(labels.hourly_rate)}</th><th>${escapeHtml(labels.hours)}</th><th>${escapeHtml(labels.amount)}</th></tr></thead>
      <tbody>${rowsHtml}</tbody>
      <tfoot><tr><td colspan="2">${escapeHtml(labels.total)}</td><td>3:30</td><td>77,00 €</td></tr></tfoot>
    </table>`;

  const paperWidth = els.templatePaper.clientWidth || 700;
  const pxPerCm = paperWidth / 21;
  els.templatePaper.style.padding = [
    configuration.page.top_margin_cm,
    configuration.page.right_margin_cm,
    configuration.page.bottom_margin_cm,
    configuration.page.left_margin_cm,
  ].map((value) => `${Number(value) * pxPerCm}px`).join(" ");
  els.templatePaper.style.fontSize = `${configuration.typography.body_size}pt`;
  els.templatePaper.style.color = configuration.typography.text_color;
  els.templatePaper.style.setProperty("--preview-header", configuration.table.header_background);
  els.templatePaper.style.setProperty("--preview-total", configuration.table.total_background);
  els.templatePaper.style.setProperty("--preview-border", configuration.table.border_color);
  els.templatePaper.style.setProperty("--preview-row-height", `${configuration.table.row_height_cm * pxPerCm}px`);

  const blockHtml = { identity, title, table };
  els.templatePaper.innerHTML = configuration.blocks
    .filter((block) => configuration.visible[block])
    .map((block) => {
      const gap = Number(configuration.spacing[`${block}_after_cm`] || 0) * pxPerCm;
      const size = block === "title" ? configuration.typography.title_size : block === "table" ? configuration.typography.table_size : configuration.typography.body_size;
      const color = block === "title" ? configuration.typography.title_color : configuration.typography.text_color;
      return `<div style="margin-bottom:${gap}px;font-size:${size}pt;color:${color}">${blockHtml[block]}</div>`;
    })
    .join("");
  const employer = els.templatePaper.querySelector(".template-preview-employer");
  if (employer) employer.style.paddingTop = `${1.1 * pxPerCm}px`;
}

function showDocumentTemplate(template) {
  state.selectedTemplateId = Number(template.id);
  state.templateDraft = cloneData(template);
  els.templateNameInput.value = template.name;
  els.templateDefaultInput.checked = Boolean(template.is_default);
  const configuration = template.configuration;
  els.templateLabelInputs.forEach((input) => {
    input.value = configuration.labels[input.dataset.templateLabel] || "";
  });
  els.templateBodySizeInput.value = configuration.typography.body_size;
  els.templateTitleSizeInput.value = configuration.typography.title_size;
  els.templateTableSizeInput.value = configuration.typography.table_size;
  els.templateTextColorInput.value = configuration.typography.text_color;
  els.templateTitleColorInput.value = configuration.typography.title_color;
  els.templateHeaderColorInput.value = configuration.table.header_background;
  els.templateTotalColorInput.value = configuration.table.total_background;
  els.templateBorderColorInput.value = configuration.table.border_color;
  els.templateMarginTopInput.value = configuration.page.top_margin_cm;
  els.templateMarginBottomInput.value = configuration.page.bottom_margin_cm;
  els.templateMarginLeftInput.value = configuration.page.left_margin_cm;
  els.templateMarginRightInput.value = configuration.page.right_margin_cm;
  els.templateIdentityGapInput.value = configuration.spacing.identity_after_cm;
  els.templateTitleGapInput.value = configuration.spacing.title_after_cm;
  els.templateRowHeightInput.value = configuration.table.row_height_cm;
  els.templateMinimumRowsInput.value = configuration.table.minimum_rows;
  setTemplateDirty(false);
  renderTemplateSelector();
  renderTemplateBlocks();
  window.requestAnimationFrame(renderTemplatePreview);
}

async function loadDocumentTemplates(preferredId = null) {
  const payload = await api("/api/document-templates");
  state.documentTemplates = payload.templates || [];
  const selected = state.documentTemplates.find((item) => Number(item.id) === Number(preferredId || state.selectedTemplateId))
    || state.documentTemplates.find((item) => item.is_default)
    || state.documentTemplates[0];
  if (selected) showDocumentTemplate(selected);
}

async function saveDocumentTemplate() {
  syncTemplateDraftFromForm(false);
  if (!state.templateDraft.name) throw new Error("Le nom du modèle est obligatoire.");
  const payload = await api(`/api/document-templates/${state.selectedTemplateId}`, {
    method: "PUT",
    body: JSON.stringify({
      name: state.templateDraft.name,
      is_default: state.templateDraft.is_default,
      configuration: state.templateDraft.configuration,
    }),
  });
  await loadDocumentTemplates(payload.template.id);
  showToast("Modèle enregistré.");
}

async function createDocumentTemplate() {
  const usedNames = new Set(state.documentTemplates.map((item) => item.name.toLowerCase()));
  let name = "Nouveau modèle";
  let suffix = 2;
  while (usedNames.has(name.toLowerCase())) {
    name = `Nouveau modèle ${suffix}`;
    suffix += 1;
  }
  const payload = await api("/api/document-templates", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
  await loadDocumentTemplates(payload.template.id);
  els.templateNameInput.focus();
  els.templateNameInput.select();
}

async function duplicateDocumentTemplate() {
  if (state.templateDirty && !window.confirm("Les modifications non enregistrées ne seront pas copiées. Continuer ?")) return;
  const payload = await api(`/api/document-templates/${state.selectedTemplateId}/duplicate`, {
    method: "POST",
    body: "{}",
  });
  await loadDocumentTemplates(payload.template.id);
  showToast("Modèle dupliqué.");
}

async function deleteDocumentTemplate() {
  const template = currentDocumentTemplate();
  if (!template || !window.confirm(`Supprimer le modèle "${template.name}" ?`)) return;
  await api(`/api/document-templates/${template.id}`, { method: "DELETE" });
  state.selectedTemplateId = null;
  state.templateDraft = null;
  await loadDocumentTemplates();
  showToast("Modèle supprimé.");
}

async function resetDocumentTemplate() {
  if (!window.confirm("Rétablir la mise en page d’origine pour ce modèle ?")) return;
  const payload = await api(`/api/document-templates/${state.selectedTemplateId}/reset`, {
    method: "POST",
    body: "{}",
  });
  await loadDocumentTemplates(payload.template.id);
  showToast("Mise en page d’origine rétablie.");
}

async function importDocumentTemplate() {
  const payload = await api("/api/document-templates/import", { method: "POST", body: "{}" });
  if (payload.cancelled) return;
  await loadDocumentTemplates(payload.template.id);
  showToast("Modèle importé.");
}

async function exportDocumentTemplate() {
  const payload = await api(`/api/document-templates/${state.selectedTemplateId}/export`, {
    method: "POST",
    body: "{}",
  });
  if (!payload.cancelled) showToast(`Modèle exporté : ${payload.path}`);
}

async function generateTemplateTestPdf() {
  syncTemplateDraftFromForm(false);
  const payload = await api("/api/document-templates/preview-pdf", {
    method: "POST",
    body: JSON.stringify({ configuration: state.templateDraft.configuration }),
  });
  if (!payload.cancelled) showToast(`PDF d’essai créé : ${payload.path}`);
}

function moveTemplateBlock(block, direction) {
  if (!state.templateDraft) return;
  const blocks = state.templateDraft.configuration.blocks;
  const index = blocks.indexOf(block);
  const destination = index + Number(direction);
  if (index < 0 || destination < 0 || destination >= blocks.length) return;
  [blocks[index], blocks[destination]] = [blocks[destination], blocks[index]];
  setTemplateDirty(true);
  renderTemplateBlocks();
  renderTemplatePreview();
}

function setActiveView(view) {
  els.tabs.forEach((tab) => tab.classList.toggle("active", tab.dataset.view === view));
  els.viewPanels.forEach((panel) => {
    panel.hidden = panel.dataset.viewPanel !== view;
  });
  if (view === "clients") {
    renderClientsTable();
  }
  if (view === "planning") {
    loadPlanning().catch((error) => showToast(error.message));
  }
  if (view === "overview") {
    loadAnnualOverview().catch((error) => showToast(error.message));
  }
  if (view === "followup") {
    loadFollowup().catch((error) => showToast(error.message));
  }
  if (view === "templates" && !state.documentTemplates.length) {
    loadDocumentTemplates().catch((error) => showToast(error.message));
  }
}

function resetForm() {
  els.editingId.value = "";
  els.formTitle.textContent = "Nouvelle intervention";
  els.form.reset();
  els.dateInput.value = new Date().toISOString().slice(0, 10);
  els.rateInput.value = state.defaultRate.toFixed(2);
  els.durationInput.value = "1:00";
  els.statusInput.value = "realisee";
  els.breakInput.value = "0";
  els.travelInput.value = "0";
  els.plannedAmountInput.value = "";
  els.receivedAmountInput.value = "";
}

function resetClientForm() {
  els.clientOriginalName.value = "";
  els.clientForm.reset();
  els.clientRateInput.value = "";
  els.clientSaveBtn.textContent = "Ajouter client";
  state.selectedClientName = "";
  state.clientReminders = [];
  resetReminderForm();
  renderClientReminders([]);
}

function formPayload() {
  const durationHours = parseDurationInput(els.durationInput.value);
  return {
    date: els.dateInput.value,
    client: els.clientInput.value,
    duration_hours: durationHours,
    hourly_rate: Number(els.rateInput.value),
    location: els.locationInput.value,
    task: els.taskInput.value,
    transmitted: els.transmittedInput.checked,
    paid: els.paidInput.checked,
    category_id: null,
    status: els.statusInput.value,
    planned_start: els.plannedStartInput.value,
    planned_end: els.plannedEndInput.value,
    actual_start: els.actualStartInput.value,
    actual_end: els.actualEndInput.value,
    break_minutes: Number(els.breakInput.value || 0),
    travel_minutes: Number(els.travelInput.value || 0),
    planned_amount: els.plannedAmountInput.value === "" ? durationHours * Number(els.rateInput.value) : Number(els.plannedAmountInput.value),
    received_amount: els.receivedAmountInput.value === "" ? (els.paidInput.checked ? durationHours * Number(els.rateInput.value) : 0) : Number(els.receivedAmountInput.value),
  };
}

function clientPayload() {
  const rawRate = els.clientRateInput.value.trim();
  const hasCustomRate = rawRate !== "" && Number(rawRate) > 0;
  return {
    name: els.clientNameInput.value,
    email: els.clientEmailInput.value,
    cesu: els.clientCesuInput.value,
    hourly_rate: hasCustomRate ? Number(rawRate) : 0,
    hourly_rate_custom: hasCustomRate,
    phone: els.clientPhoneInput.value,
    address: els.clientAddressInput.value,
  };
}

function loadIntoForm(row) {
  els.editingId.value = row.id;
  els.formTitle.textContent = "Modifier l'intervention";
  els.dateInput.value = row.date;
  els.clientInput.value = row.client;
  els.durationInput.value = formatDurationInput(row.duration_hours);
  els.rateInput.value = row.hourly_rate;
  els.locationInput.value = row.location || "";
  els.taskInput.value = row.task || "";
  els.transmittedInput.checked = row.transmitted;
  els.paidInput.checked = row.paid;
  els.statusInput.value = row.status === "realized" ? "realisee" : (row.status || "realisee");
  els.plannedStartInput.value = row.planned_start || "";
  els.plannedEndInput.value = row.planned_end || "";
  els.actualStartInput.value = row.actual_start || "";
  els.actualEndInput.value = row.actual_end || "";
  els.breakInput.value = row.break_minutes || 0;
  els.travelInput.value = row.travel_minutes || 0;
  els.plannedAmountInput.value = row.planned_amount || "";
  els.receivedAmountInput.value = row.received_amount || "";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function loadIntoClientForm(client) {
  els.clientOriginalName.value = client.name;
  els.clientNameInput.value = client.name || "";
  els.clientEmailInput.value = client.email || "";
  els.clientCesuInput.value = client.cesu || "";
  els.clientRateInput.value =
    client.hourly_rate_custom && Number(client.hourly_rate || 0) > 0 ? Number(client.hourly_rate).toFixed(2) : "";
  els.clientPhoneInput.value = client.phone || "";
  els.clientAddressInput.value = client.address || "";
  els.clientSaveBtn.textContent = "Modifier client";
  state.selectedClientName = client.name;
  loadClientReminders(client.name).catch((error) => showToast(error.message));
  setActiveView("clients");
}

function resetReminderForm() {
  els.reminderId.value = "";
  els.reminderForm.reset();
  els.reminderDateInput.value = new Date().toISOString().slice(0, 10);
  els.reminderIntervalInput.value = "1";
  els.reminderAnticipationInput.value = "7";
  els.reminderUnitInput.value = "days";
  els.reminderActiveInput.checked = true;
  els.reminderSaveBtn.textContent = "Enregistrer le rappel";
  els.reminderClientHint.textContent = state.selectedClientName
    ? `Rappels pour ${state.selectedClientName}.`
    : "Sélectionne ou enregistre un client pour ajouter un rappel.";
}

function reminderPayload() {
  return {
    client_name: state.selectedClientName,
    title: els.reminderTitleInput.value.trim(),
    description: els.reminderDescriptionInput.value.trim(),
    reference_date: els.reminderDateInput.value,
    due_time: els.reminderTimeInput.value,
    recurrence_type: els.reminderRecurrenceInput.value,
    recurrence_interval: Number(els.reminderIntervalInput.value),
    anticipation_value: Number(els.reminderAnticipationInput.value),
    anticipation_unit: els.reminderUnitInput.value,
    is_active: els.reminderActiveInput.checked,
  };
}

function reminderCard(item, compact = false) {
  const due = `${dateFr(item.due_date)}${item.due_time ? ` à ${item.due_time}` : ""}`;
  const stateLabel = item.state === "late" ? "En retard" : item.state === "today" ? "Aujourd'hui" : "À venir";
  const managementActions = compact
    ? ""
    : `<button class="icon-btn" title="Modifier le rappel" data-edit-reminder="${item.reminder_id}">✎</button>
       <button class="icon-btn delete-btn" title="Supprimer le rappel" data-delete-reminder="${item.reminder_id}">×</button>`;
  return `<article class="reminder-card ${escapeHtml(item.state || "")}">
    <div><strong>${escapeHtml(item.title)}</strong><span>${escapeHtml(item.client_name || "")}</span></div>
    <p>${escapeHtml(item.description || due)}</p>
    <small>${compact ? due : `${due} · ${stateLabel}`}</small>
    <div class="row-actions"><button class="icon-btn" title="Marquer comme traité" data-complete-reminder="${item.reminder_id}" data-occurrence-id="${item.id}">✓</button>${managementActions}</div>
  </article>`;
}

function renderPlanning() {
  const render = (items, target, empty) => {
    target.innerHTML = items.length ? items.map((item) => reminderCard(item, true)).join("") : `<p class="empty-note">${empty}</p>`;
  };
  render(state.reminders.late || [], els.planningLate, "Aucun rappel en retard.");
  render(state.reminders.today_items || [], els.planningToday, "Rien à traiter aujourd'hui.");
  render(state.reminders.upcoming || [], els.planningUpcoming, "Aucun rappel à venir.");
}

function renderClientReminders(reminders) {
  if (!state.selectedClientName) {
    els.clientReminders.innerHTML = "";
    return;
  }
  const cards = reminders.flatMap((reminder) => (reminder.occurrences || []).filter((item) => item.status === "pending").slice(0, 3));
  els.clientReminders.innerHTML = cards.length
    ? cards.map((item) => reminderCard(item)).join("")
    : `<p class="empty-note">Aucun rappel actif pour ce client.</p>`;
}

async function loadPlanning() {
  const payload = await api("/api/reminders/overview");
  state.reminders = payload;
  renderPlanning();
}

async function loadClientReminders(clientName) {
  if (!clientName) return;
  const payload = await api(`/api/reminders?client=${encodeURIComponent(clientName)}`);
  state.clientReminders = payload.reminders || [];
  renderClientReminders(state.clientReminders);
  resetReminderForm();
}

async function refreshReminders() {
  await Promise.all([loadPlanning(), state.selectedClientName ? loadClientReminders(state.selectedClientName) : Promise.resolve()]);
}

async function loadClients() {
  const payload = await api("/api/clients");
  state.clients = payload.clients;
  renderClients();
}

async function loadMonth() {
  const year = selectedYear();
  const month = selectedMonth();
  const [summary, interventions] = await Promise.all([
    api(`/api/summary?year=${year}&month=${month}`),
    api(`/api/interventions?year=${year}&month=${month}`),
  ]);
  state.interventions = interventions.interventions;
  els.metricInterventions.textContent = summary.interventions;
  els.metricClients.textContent = summary.clients;
  els.metricHours.textContent = summary.hours_label;
  els.metricNet.textContent = euro(summary.amount_net);
  els.monthTitle.textContent = `${selectedMonthName()} ${year}`;
  const profileLabel = currentProfile()?.label;
  els.statusLine.textContent = `${profileLabel ? `${profileLabel} - ` : ""}${summary.hours_label} - ${summary.clients} client(s) - ${euro(summary.amount_net)}`;
  renderInterventions();
}

function compactMoney(value) {
  return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(Number(value || 0));
}

function formatVariation(value, percent, formatter) {
  const prefix = value > 0 ? "+" : value < 0 ? "-" : "";
  const percentage = percent === null || percent === undefined ? "" : ` (${prefix}${Math.abs(percent).toLocaleString("fr-FR")} %)`;
  return `${prefix}${formatter(Math.abs(value))}${percentage}`;
}

function renderBarChart(element, scaleElement, points, valueKey, label) {
  const maximum = Math.max(
    ...points.flatMap((item) => [Number(item.current[valueKey] || 0), Number(item.reference[valueKey] || 0)]),
    0,
  );
  scaleElement.textContent = maximum ? `Maximum : ${label(maximum)}` : "Aucune donnée";
  element.style.gridTemplateColumns = `repeat(${Math.max(points.length, 1)}, minmax(42px, 1fr))`;
  element.style.minWidth = `${Math.max(points.length * 50, 360)}px`;
  element.innerHTML = points
    .map((item) => {
      const current = Number(item.current[valueKey] || 0);
      const reference = Number(item.reference[valueKey] || 0);
      const currentHeight = maximum ? Math.max(3, Math.round((current / maximum) * 100)) : 3;
      const referenceHeight = maximum ? Math.max(3, Math.round((reference / maximum) * 100)) : 3;
      return `
        <div class="bar-chart-item" title="${escapeHtml(item.label)} - choisi : ${escapeHtml(label(current))} ; référence : ${escapeHtml(label(reference))}">
          <span class="bar-chart-column"><i class="bar-current" style="height: ${currentHeight}%"></i><i class="bar-reference" style="height: ${referenceHeight}%"></i></span>
          <span class="bar-chart-label">${escapeHtml(chartShortLabel(item.label))}</span>
        </div>`;
    })
    .join("");
}

function renderComparisonOverview() {
  const overview = state.overview;
  if (!overview) return;
  const totals = overview.current_totals || {};
  const referenceTotals = overview.reference_totals || {};
  const selectedLabel = `${dateFr(overview.start)} au ${dateFr(overview.end)}`;
  const referenceLabel = `${dateFr(overview.reference_start)} au ${dateFr(overview.reference_end)}`;
  if (totals.interventions) {
    els.overviewBusiest.textContent = `Période choisie : ${selectedLabel}`;
    els.overviewDetail.textContent = `Comparaison avec ${referenceLabel}`;
  } else {
    els.overviewBusiest.textContent = "Aucune intervention sur la période choisie";
    els.overviewDetail.textContent = `Référence : ${referenceLabel}`;
  }
  const hoursVariation = overview.variations.hours || {};
  const netVariation = overview.variations.amount_net || {};
  const interventionsVariation = overview.variations.interventions || {};
  els.overviewHoursVariation.textContent = formatVariation(hoursVariation.difference || 0, hoursVariation.percent, durationLabel);
  els.overviewNetVariation.textContent = formatVariation(netVariation.difference || 0, netVariation.percent, euro);
  els.overviewInterventionsVariation.textContent = formatVariation(interventionsVariation.difference || 0, interventionsVariation.percent, (value) => String(value));
  els.overviewHoursReference.textContent = `Référence : ${referenceTotals.hours_label || "00:00"}`;
  els.overviewNetReference.textContent = `Référence : ${euro(referenceTotals.amount_net)}`;
  els.overviewInterventionsReference.textContent = `Référence : ${referenceTotals.interventions || 0}`;
  renderBarChart(els.netChart, els.netChartScale, overview.points, "amount_net", (value) => euro(value));
  renderBarChart(els.hoursChart, els.hoursChartScale, overview.points, "hours", (value) => durationLabel(value));
  els.overviewBody.innerHTML = overview.points
    .filter((item) => item.current.interventions || item.reference.interventions)
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.label)}</td>
          <td>${durationLabel(item.current.hours)}</td>
          <td>${durationLabel(item.reference.hours)}</td>
          <td>${euro(item.current.amount_net)}</td>
          <td>${euro(item.reference.amount_net)}</td>
          <td>${formatVariation(item.current.amount_net - item.reference.amount_net, null, euro)}</td>
          <td>${item.current.interventions}</td>
        </tr>`,
    ).join("") || `<tr><td class="empty-row" colspan="7">Aucune intervention pour ces périodes</td></tr>`;
}

async function loadOverview() {
  if (!els.overviewStart.value || !els.overviewEnd.value || state.overviewYear !== selectedYear()) {
    els.overviewStart.value = `${selectedYear()}-01-01`;
    els.overviewEnd.value = `${selectedYear()}-12-31`;
    state.overviewYear = selectedYear();
  }
  const params = new URLSearchParams({
    start: els.overviewStart.value,
    end: els.overviewEnd.value,
    granularity: els.overviewGranularity.value,
    reference: els.overviewReference.value,
  });
  const overview = await api(`/api/comparison-overview?${params.toString()}`);
  state.overview = overview;
  renderComparisonOverview();
}

function shortHours(value) {
  return `${Number(value || 0).toLocaleString("fr-FR", { maximumFractionDigits: 2 })} h`;
}

function chartShortLabel(label) {
  const month = String(label).match(/^([A-Za-zÀ-ÿ]+) \d{4}$/);
  if (month) return month[1].slice(0, 3);
  if (String(label).startsWith("Semaine du ")) return `S. ${String(label).slice(-5)}`;
  return String(label);
}

function renderAnnualLineChart(periods) {
  const width = Math.max(760, periods.length * 68);
  const height = 270;
  const padding = { top: 36, right: 20, bottom: 42, left: 52 };
  const maximum = Math.max(...periods.map((item) => Number(item.amount_net || 0)), 0);
  const chartHeight = height - padding.top - padding.bottom;
  const chartWidth = width - padding.left - padding.right;
  const y = (value) => padding.top + chartHeight - (maximum ? (value / maximum) * chartHeight : 0);
  const x = (index) => padding.left + (chartWidth * index) / Math.max(periods.length - 1, 1);
  const grid = [0, 0.25, 0.5, 0.75, 1]
    .map((ratio) => {
      const value = maximum * ratio;
      const lineY = y(value);
      return `<line x1="${padding.left}" y1="${lineY}" x2="${width - padding.right}" y2="${lineY}" class="annual-grid-line" /><text x="${padding.left - 8}" y="${lineY + 4}" text-anchor="end" class="annual-axis-label">${compactMoney(value)}</text>`;
    })
    .join("");
  const points = periods.map((item, index) => `${x(index)},${y(Number(item.amount_net || 0))}`).join(" ");
  const labelStep = Math.max(1, Math.ceil(periods.length / 12));
  const dots = periods
    .map((item, index) => {
      const value = Number(item.amount_net || 0);
      const valueLabel = value && periods.length <= 12 ? `<text x="${x(index)}" y="${Math.max(y(value) - 12, 16)}" text-anchor="middle" class="annual-point-label">${compactMoney(value)} €</text>` : "";
      return `${valueLabel}<circle cx="${x(index)}" cy="${y(value)}" r="${value ? 5 : 3}" class="annual-point ${value ? "has-value" : ""}" />`;
    })
    .join("");
  const labels = periods
    .map((item, index) => index % labelStep === 0 || index === periods.length - 1 ? `<text x="${x(index)}" y="${height - 12}" text-anchor="middle" class="annual-month-label">${escapeHtml(chartShortLabel(item.label))}</text>` : "")
    .join("");
  els.annualNetChart.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Évolution du montant net">${grid}<polyline points="${points}" class="annual-line" />${dots}${labels}</svg>`;
}

function renderAnnualHoursChart(periods) {
  const activePeriods = periods.filter((item) => Number(item.hours || 0) > 0);
  const maximum = Math.max(...periods.map((item) => Number(item.hours || 0)), 0);
  if (!activePeriods.length) {
    els.annualHoursChart.style.minWidth = "";
    els.annualHoursChart.innerHTML = `<p class="empty-note">Aucune intervention cette année.</p>`;
    els.annualInsight.textContent = "Aucune intervention cette année.";
    return;
  }
  els.annualHoursChart.style.minWidth = `${Math.max(periods.length * 76, 320)}px`;
  els.annualHoursChart.innerHTML = periods
    .map((item) => {
      const height = Math.max(4, Math.round((Number(item.hours) / maximum) * 100));
      return `<div class="annual-hours-item" title="${escapeHtml(item.label)} : ${shortHours(item.hours)}"><strong>${shortHours(item.hours)}</strong><span><i style="height:${height}%"></i></span><b>${escapeHtml(chartShortLabel(item.label))}</b></div>`;
    })
    .join("");
  const busiest = activePeriods.reduce((best, item) => (Number(item.hours) > Number(best.hours) ? item : best));
  const unit = { day: "jour", week: "semaine", month: "mois", year: "année" }[state.annualOverview?.granularity] || "période";
  els.annualInsight.textContent = `${busiest.label} est le ${unit} le plus actif.`;
}

function renderAnnualOverview() {
  const overview = state.annualOverview;
  if (!overview) return;
  const totals = overview.totals || {};
  const names = { day: "journalière", week: "hebdomadaire", month: "mensuelle", year: "annuelle" };
  const periods = overview.periods || [];
  els.annualTitle.textContent = `Bilan d'activité ${overview.scope_label}`;
  els.annualSubtitle.textContent = `Évolution ${names[overview.granularity] || ""} - données Easy CESU`;
  els.overviewNet.textContent = euro(totals.amount_net);
  els.overviewInterventions.textContent = totals.interventions || 0;
  els.overviewHours.textContent = totals.hours_label || "00:00";
  els.overviewAverage.textContent = totals.clients_periods || 0;
  els.overviewAverageLabel.textContent = overview.granularity === "month" ? "Clients-mois" : `Clients-${overview.granularity === "day" ? "jours" : overview.granularity === "week" ? "semaines" : "années"}`;
  els.annualNetChartTitle.textContent = `Évolution du montant net ${names[overview.granularity] || ""}`;
  els.annualHoursChartTitle.textContent = `Comparaison des heures ${names[overview.granularity] || ""}`;
  renderAnnualLineChart(periods);
  renderAnnualHoursChart(periods);
}

async function loadAnnualOverview() {
  if (state.overviewYear !== selectedYear()) {
    els.overviewStart.value = `${selectedYear()}-01-01`;
    els.overviewEnd.value = `${selectedYear()}-12-31`;
    state.overviewYear = selectedYear();
    state.overview = null;
  }
  const params = new URLSearchParams({ year: selectedYear(), month: selectedMonth(), granularity: els.annualGranularity.value });
  state.annualOverview = await api(`/api/activity-overview?${params.toString()}`);
  renderAnnualOverview();
}

function renderInterventions() {
  const term = els.searchInput.value.trim().toLowerCase();
  const rows = state.interventions.filter((row) => {
    const haystack = `${row.date} ${row.client} ${row.task} ${row.location}`.toLowerCase();
    return !term || haystack.includes(term);
  });
  if (!rows.length) {
    els.interventionsBody.innerHTML = `<tr><td class="empty-row" colspan="6">Aucune intervention</td></tr>`;
    return;
  }
  els.interventionsBody.innerHTML = rows
    .map(
      (row) => `
      <tr>
        <td>${dateFr(row.date)}</td>
        <td>${escapeHtml(row.client)}</td>
        <td>${durationLabel(row.duration_hours)}</td>
        <td>${euro(row.amount_net)}</td>
        <td>${escapeHtml(row.task || row.location || "")}</td>
        <td>
          <div class="row-actions">
            <button class="icon-btn" title="Modifier" data-edit="${row.id}">✎</button>
            <button class="icon-btn delete-btn" title="Supprimer" data-delete="${row.id}">×</button>
          </div>
        </td>
      </tr>`,
    )
    .join("");
}

async function saveIntervention(event) {
  event.preventDefault();
  els.saveBtn.disabled = true;
  try {
    const id = els.editingId.value;
    const payload = formPayload();
    if (!Number.isFinite(payload.duration_hours) || payload.duration_hours < 0.5) {
      showToast("Saisis une durée valide, par exemple 2:30.");
      els.durationInput.focus();
      return;
    }
    if (id) {
      await api(`/api/interventions/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      showToast("Intervention modifiée.");
    } else {
      await api("/api/interventions", { method: "POST", body: JSON.stringify(payload) });
      showToast("Intervention enregistrée.");
    }
    resetForm();
    await loadClients();
    await loadMonth();
  } catch (error) {
    showToast(error.message);
  } finally {
    els.saveBtn.disabled = false;
  }
}

async function deleteIntervention(id) {
  await api(`/api/interventions/${id}`, { method: "DELETE" });
  showToast("Intervention supprimée.");
  await loadMonth();
}

async function deleteClient(name) {
  if (!window.confirm(`Supprimer la fiche client "${name}" ? Les interventions déjà saisies restent conservées.`)) {
    return;
  }
  await api(`/api/clients/${encodeURIComponent(name)}`, { method: "DELETE" });
  showToast("Client supprimé.");
  resetClientForm();
  await loadClients();
}

async function saveSettings(options = {}) {
  const wasCreatingProfile = state.creatingProfile;
  const endpoint = state.creatingProfile
    ? "/api/profiles"
    : `/api/profiles/${encodeURIComponent(state.activeProfileId)}`;
  const payload = await api(endpoint, {
    method: state.creatingProfile ? "POST" : "PUT",
    body: JSON.stringify(profilePayload()),
  });
  if (payload.clients) {
    applyBootstrap(payload, { keepFilters: !wasCreatingProfile });
  } else if (payload.settings) {
    applySettings(payload.settings);
  }
  renderClients();
  applySelectedClientDefaults();
  await loadMonth();
  if (!options.silent) {
    showToast(wasCreatingProfile ? "Compte créé." : "Réglages enregistrés.");
  }
  if (wasCreatingProfile) {
    clearDocumentTemplateState();
    showSetupAssistant("account");
  }
  return payload.settings || payload;
}

async function browseNotesDir() {
  els.browseNotesDirBtn.disabled = true;
  showToast("Ouverture du choix de dossier Windows...");
  try {
    const payload = await api("/api/select-notes-dir", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    if (payload.cancelled) {
      showToast("Choix du dossier annulé.");
    } else {
      showToast("Dossier de génération enregistré.");
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    els.browseNotesDirBtn.disabled = false;
  }
}

async function browseDataDir() {
  els.browseDataDirBtn.disabled = true;
  showToast("Ouverture du choix de dossier Windows...");
  try {
    const payload = await api("/api/select-data-dir", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    if (payload.cancelled) {
      showToast("Choix du dossier annulé.");
    } else {
      showToast("Dossier de données enregistré.");
      await loadClients();
      await loadMonth();
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    els.browseDataDirBtn.disabled = false;
  }
}

async function selectDatabaseFile() {
  els.selectDatabaseFileBtn.disabled = true;
  showToast("Choisis le fichier de base Easy CESU...");
  try {
    const payload = await api("/api/select-database-file", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    if (payload.clients) {
      state.clients = payload.clients;
      renderClients();
    }
    if (payload.cancelled) {
      showToast("Choix de la base annulé.");
    } else {
      showToast("Base de données sélectionnée.");
      await loadClients();
      await loadMonth();
      showSetupAssistant("database");
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    els.selectDatabaseFileBtn.disabled = false;
  }
}

async function importDatabase() {
  els.importDatabaseBtn.disabled = true;
  showToast("Choisis la base Easy CESU à importer...");
  try {
    const payload = await api("/api/import-backup", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    if (payload.clients) {
      state.clients = payload.clients;
      renderClients();
    }
    if (payload.cancelled) {
      showToast("Import annulé.");
    } else {
      await loadClients();
      await loadMonth();
      const backupLine = payload.backup_before_restore ? `\nSauvegarde de précaution : ${payload.backup_before_restore}` : "";
      const transferLine = payload.from_transfer_kit ? "\nSauvegarde trouvée automatiquement dans le kit de transfert." : "";
      showToast(`Sauvegarde restaurée\n${payload.restored_profile?.label || "Compte importé"}${transferLine}${backupLine}`);
      showSetupAssistant("import");
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    els.importDatabaseBtn.disabled = false;
  }
}

async function configureFolders(options = {}) {
  if (!options.skipIntro) {
    const confirmed = window.confirm(
      "Choisir un dossier principal Easy CESU ?\n\nL'application y rangera automatiquement la base, les notes et les exports de ce compte.",
    );
    if (!confirmed) return;
  }
  els.setupFoldersBtn.disabled = true;
  els.setupAssistantStartBtn.disabled = true;
  els.setupAssistantLaterBtn.disabled = true;
  try {
    showToast("Choisis où créer le dossier principal Easy CESU...");
    const payload = await api("/api/select-workspace-root", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    if (payload.cancelled) {
      showToast("Configuration annulée. Tu pourras la reprendre plus tard.");
      return false;
    }
    if (els.setupAssistantDialog.open) {
      state.setupStep = 5;
      renderSetupStep();
    }
    await loadClients();
    await loadMonth();
    showToast(`Dossiers configurés\n${payload.workspace_root}`);
    return true;
  } catch (error) {
    showToast(error.message);
    return false;
  } finally {
    els.setupFoldersBtn.disabled = false;
    els.setupAssistantStartBtn.disabled = false;
    els.setupAssistantLaterBtn.disabled = false;
  }
}

async function browseSourceDir() {
  els.browseSourceDirBtn.disabled = true;
  showToast("Ouverture du choix de dossier Windows...");
  try {
    const payload = await api("/api/select-source-dir", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    showToast(payload.cancelled ? "Choix du dossier annulé." : "Dossier source enregistré.");
  } catch (error) {
    showToast(error.message);
  } finally {
    els.browseSourceDirBtn.disabled = false;
  }
}

async function browseClientsFile() {
  els.browseClientsFileBtn.disabled = true;
  showToast("Ouverture du choix de fichier Windows...");
  try {
    const payload = await api("/api/select-clients-file", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    showToast(payload.cancelled ? "Choix du fichier annulé." : "Fichier clients enregistré.");
  } catch (error) {
    showToast(error.message);
  } finally {
    els.browseClientsFileBtn.disabled = false;
  }
}

async function browseExportDir() {
  els.browseExportDirBtn.disabled = true;
  showToast("Ouverture du choix de dossier Windows...");
  try {
    const payload = await api("/api/select-export-dir", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    if (payload.cancelled) {
      showToast("Choix du dossier annulé.");
    } else {
      showToast("Dossier des exports enregistré.");
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    els.browseExportDirBtn.disabled = false;
  }
}

async function backupDatabase() {
  els.backupDatabaseBtn.disabled = true;
  showToast("Choisis le dossier où exporter la copie...");
  try {
    const payload = await api("/api/export-backup", { method: "POST", body: "{}" });
    applySettings(payload.settings);
    showToast(payload.cancelled ? "Export annulé." : `Sauvegarde ZIP créée\n${payload.backup}`);
  } catch (error) {
    showToast(error.message);
  } finally {
    els.backupDatabaseBtn.disabled = false;
  }
}

async function deleteCurrentProfile() {
  const profile = currentProfile();
  if (!profile || state.creatingProfile) return;
  if (!window.confirm(`Supprimer le compte "${profile.label}" de l'application ?\n\nLa base de données ne sera pas effacée.`)) {
    return;
  }
  const payload = await api(`/api/profiles/${encodeURIComponent(profile.id)}`, { method: "DELETE" });
  applyBootstrap(payload);
  clearDocumentTemplateState();
  await loadMonth();
  showToast("Compte supprimé de l'application.");
}

async function generateNotes() {
  els.generateBtn.disabled = true;
  try {
    showToast("Choisis le dossier où créer les notes...");
    const selected = await api("/api/select-notes-dir", { method: "POST", body: "{}" });
    applySettings(selected.settings);
    if (selected.cancelled) {
      showToast("Génération annulée.");
      return;
    }
    const payload = await api("/api/generate-month", {
      method: "POST",
      body: JSON.stringify({
        year: selectedYear(),
        month: selectedMonth(),
        replace: false,
        notes_intervention_dir: selected.notes_intervention_dir || els.notesDirInput.value.trim(),
      }),
    });
    state.notesDir = payload.output_base || state.notesDir;
    els.notesDirInput.value = state.notesDir;
    const created = payload.notes.created.length;
    const skipped = payload.notes.skipped.length;
    const errors = payload.notes.errors.length;
    showToast(`Notes générées pour ${payload.month_label}\nCréées : ${created}\nDéjà présentes : ${skipped}\nErreurs : ${errors}\n${payload.output_dir}`);
  } catch (error) {
    showToast(error.message);
  } finally {
    els.generateBtn.disabled = false;
  }
}

async function exportYear() {
  els.exportBtn.disabled = true;
  try {
    showToast("Choisis le dossier où créer le bilan Excel...");
    const selected = await api("/api/select-export-dir", { method: "POST", body: "{}" });
    applySettings(selected.settings);
    if (selected.cancelled) {
      showToast("Export annulé.");
      return;
    }
    const payload = await api("/api/export-year", {
      method: "POST",
      body: JSON.stringify({ year: selectedYear(), export_dir: selected.export_dir || els.exportDirInput.value.trim() }),
    });
    showToast(`Bilan créé\n${payload.xlsx}`);
  } catch (error) {
    showToast(error.message);
  } finally {
    els.exportBtn.disabled = false;
  }
}

async function saveClient(event) {
  event.preventDefault();
  els.clientSaveBtn.disabled = true;
  try {
    const originalName = els.clientOriginalName.value;
    const payload = clientPayload();
    if (originalName) {
      await api(`/api/clients/${encodeURIComponent(originalName)}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Client modifié.");
    } else {
      await api("/api/clients", { method: "POST", body: JSON.stringify(payload) });
      showToast("Client ajouté.");
    }
    const nameChanged = originalName && originalName !== payload.name.trim();
    state.selectedClientName = payload.name.trim();
    await loadClients();
    await loadClientReminders(state.selectedClientName);
    if (els.clientInput.value === payload.name.trim()) {
      applySelectedClientDefaults();
    }
    if (nameChanged) {
      await loadMonth();
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    els.clientSaveBtn.disabled = false;
  }
}

async function saveReminder(event) {
  event.preventDefault();
  if (!state.selectedClientName) {
    showToast("Enregistre ou sélectionne d'abord le client.");
    return;
  }
  els.reminderSaveBtn.disabled = true;
  try {
    const reminderId = els.reminderId.value;
    const payload = reminderPayload();
    await api(reminderId ? `/api/reminders/${reminderId}` : "/api/reminders", {
      method: reminderId ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    showToast(reminderId ? "Rappel modifié." : "Rappel enregistré.");
    await refreshReminders();
  } catch (error) {
    showToast(error.message);
  } finally {
    els.reminderSaveBtn.disabled = false;
  }
}

async function completeReminder(reminderId, occurrenceId) {
  await api(`/api/reminders/${reminderId}/occurrences`, {
    method: "POST",
    body: JSON.stringify({ occurrence_id: Number(occurrenceId), status: "completed" }),
  });
  showToast("Rappel marqué comme traité.");
  await refreshReminders();
}

function loadReminderIntoForm(reminderId) {
  const reminder = state.clientReminders.find((item) => String(item.id) === String(reminderId));
  if (!reminder) return;
  els.reminderId.value = reminder.id;
  els.reminderTitleInput.value = reminder.title || "";
  els.reminderDateInput.value = reminder.reference_date || "";
  els.reminderTimeInput.value = reminder.due_time || "";
  els.reminderRecurrenceInput.value = reminder.recurrence_type || "once";
  els.reminderIntervalInput.value = reminder.recurrence_interval || 1;
  els.reminderAnticipationInput.value = reminder.anticipation_value || 0;
  els.reminderUnitInput.value = reminder.anticipation_unit || "days";
  els.reminderDescriptionInput.value = reminder.description || "";
  els.reminderActiveInput.checked = Boolean(reminder.is_active);
  els.reminderSaveBtn.textContent = "Modifier le rappel";
  els.reminderTitleInput.focus();
}

async function deleteReminder(reminderId) {
  if (!window.confirm("Supprimer ce rappel et son historique ?")) return;
  await api(`/api/reminders/${reminderId}`, { method: "DELETE" });
  showToast("Rappel supprimé.");
  await refreshReminders();
}

async function refreshClients() {
  els.refreshClientsBtn.disabled = true;
  try {
    const payload = await api("/api/refresh-clients", { method: "POST", body: "{}" });
    state.clients = payload.clients;
    renderClients();
    showToast("Liste clients mise à jour.");
  } catch (error) {
    showToast(error.message);
  } finally {
    els.refreshClientsBtn.disabled = false;
  }
}

function beginNewProfile() {
  setProfileEditorMode(true);
  setProfileForm({
    label: "",
    name: "",
    address: "",
    phone: "",
    email: "",
    ss_number: "",
    birth_info: "",
    default_hourly_rate: state.defaultRate,
    suivi_paye_dir: "",
    suivi_paye_pattern: "Suivi de paye {year}.xlsx",
    fichier_clients: "",
    data_dir: "",
    notes_intervention_dir: "",
    export_dir: "",
  });
  els.profileLabelInput.focus();
}

function cancelNewProfile() {
  setProfileEditorMode(false);
  setProfileForm(currentProfile() || {});
}

async function switchActiveProfile(profileId) {
  if (!profileId || profileId === "__new" || profileId === state.activeProfileId) {
    renderProfiles();
    return;
  }
  const payload = await api("/api/switch-profile", {
    method: "POST",
    body: JSON.stringify({ profile_id: profileId }),
  });
  applyBootstrap(payload);
  clearDocumentTemplateState();
  await loadMonth();
  showToast("Compte actif changé.");
}

function activityLabel(value) {
  return {
    jardinage: "Jardinage", bricolage: "Bricolage", menage: "Ménage", aide_a_domicile: "Aide à domicile",
    garde_d_enfants: "Garde d'enfants", soutien_scolaire: "Soutien scolaire", accompagnement: "Accompagnement",
    assistance_administrative: "Assistance administrative", informatique: "Informatique", autre: "Autre",
  }[value] || "Toutes activités";
}

function renderFollowup() {
  els.notesList.innerHTML = state.notes.length
    ? state.notes.map((item) => `<article class="followup-item"><div><strong>${escapeHtml(item.client_name)}</strong><span>${escapeHtml(item.body)}</span><small>${escapeHtml(item.status.replaceAll("_", " "))}${item.carry_forward ? " · à reporter" : ""}</small></div><button class="icon-btn delete-btn" title="Supprimer" data-delete-note="${item.id}">×</button></article>`).join("")
    : `<p class="empty-note">Aucune note à suivre.</p>`;
  els.paymentsList.innerHTML = state.payments.length
    ? state.payments.map((item) => `<article class="followup-item"><div><strong>${escapeHtml(item.client_name)} · ${euro(item.expected_amount)}</strong><span>${escapeHtml(item.payment_method || "Paiement à suivre")}${item.expected_date ? ` · ${dateFr(item.expected_date)}` : ""}</span></div><button class="secondary small-action" data-receive-payment="${item.id}">Reçu</button></article>`).join("")
    : `<p class="empty-note">Aucun paiement en attente.</p>`;
}

async function loadFollowup() {
  const [notes, payments] = await Promise.all([
    api("/api/notes?status=a_faire"), api("/api/pending-payments"),
  ]);
  state.notes = notes.notes;
  state.payments = payments.payments.filter((item) => !["recu", "annule"].includes(item.status));
  renderFollowup();
}

async function saveNote(event) {
  event.preventDefault();
  await api("/api/notes", { method: "POST", body: JSON.stringify({
    client_name: els.noteClientInput.value, body: els.noteBodyInput.value, category: els.noteCategoryInput.value,
    priority: els.notePriorityInput.value, status: els.noteCategoryInput.value === "a_faire" ? "a_faire" : "information",
    carry_forward: els.noteCarryInput.checked,
  }) });
  els.noteForm.reset();
  await loadFollowup();
  showToast("Note enregistrée.");
}

async function savePayment(event) {
  event.preventDefault();
  await api("/api/pending-payments", { method: "POST", body: JSON.stringify({
    client_name: els.paymentClientInput.value, expected_amount: Number(els.paymentAmountInput.value),
    expected_date: els.paymentDateInput.value, payment_method: els.paymentMethodInput.value,
  }) });
  els.paymentForm.reset();
  await loadFollowup();
  showToast("Paiement à suivre créé.");
}

function bindEvents() {
  els.displayModeSelect.addEventListener("change", () => {
    const scale = applyDisplayMode(els.displayModeSelect.value);
    showToast(`Affichage réglé à ${Math.round(scale * 100)} %. Ce choix reste propre à cet ordinateur.`);
  });
  els.form.addEventListener("submit", saveIntervention);
  els.resetBtn.addEventListener("click", resetForm);
  els.durationInput.addEventListener("blur", () => {
    const duration = parseDurationInput(els.durationInput.value);
    if (Number.isFinite(duration) && duration >= 0.5) {
      els.durationInput.value = formatDurationInput(duration);
    }
  });
  els.yearFilter.addEventListener("change", async () => {
    await loadMonth();
    state.overviewYear = null;
    state.annualOverview = null;
    if (!els.overviewPanel.hidden) {
      await loadAnnualOverview();
    }
  });
  els.monthFilter.addEventListener("change", async () => {
    await loadMonth();
    if (!els.overviewPanel.hidden && els.annualGranularity.value === "day") {
      await loadAnnualOverview();
    }
  });
  els.searchInput.addEventListener("input", renderInterventions);
  els.clientSearchInput.addEventListener("input", renderClientsTable);
  els.generateBtn.addEventListener("click", generateNotes);
  els.exportBtn.addEventListener("click", exportYear);
  els.quickProfileSelect.addEventListener("change", () => {
    switchActiveProfile(els.quickProfileSelect.value).catch((error) => showToast(error.message));
  });
  els.browseSourceDirBtn.addEventListener("click", browseSourceDir);
  els.browseClientsFileBtn.addEventListener("click", browseClientsFile);
  els.setupFoldersBtn.addEventListener("click", () => configureFolders());
  els.browseDataDirBtn.addEventListener("click", browseDataDir);
  els.selectDatabaseFileBtn.addEventListener("click", selectDatabaseFile);
  els.importDatabaseBtn.addEventListener("click", importDatabase);
  els.backupDatabaseBtn.addEventListener("click", backupDatabase);
  els.setupAssistantStartBtn.addEventListener("click", () => configureFolders({ skipIntro: true }));
  els.setupAssistantEmptyBtn.addEventListener("click", () => {
    advanceSetupAssistant().catch((error) => showToast(error.message));
  });
  els.setupAssistantRestoreBtn.addEventListener("click", importDatabase);
  els.setupAssistantNextBtn.addEventListener("click", () => advanceSetupAssistant().catch((error) => showToast(error.message)));
  els.setupActivityInput.addEventListener("change", () => {
    const activity = els.setupActivityInput.value;
    applyProfileIcon(activity === "autre" ? "generique" : activity);
  });
  els.setupAssistantPreviousBtn.addEventListener("click", () => {
    state.setupStep = Math.max(1, state.setupStep - 1);
    renderSetupStep();
  });
  els.setupAssistantLaterBtn.addEventListener("click", hideSetupAssistant);
  els.browseNotesDirBtn.addEventListener("click", browseNotesDir);
  els.browseExportDirBtn.addEventListener("click", browseExportDir);
  els.deleteProfileBtn.addEventListener("click", () => {
    deleteCurrentProfile().catch((error) => showToast(error.message));
  });
  els.saveSettingsBtn.addEventListener("click", () => {
    saveSettings().catch((error) => showToast(error.message));
  });
  els.githubSourceBtn.addEventListener("click", () => openExternal("github_repository").catch((error) => showToast(error.message)));
  els.githubStarBtn.addEventListener("click", () => openExternal("github_star").catch((error) => showToast(error.message)));
  els.githubIssueBtn.addEventListener("click", () => openExternal("github_issues").catch((error) => showToast(error.message)));
  els.paypalSupportBtn.addEventListener("click", showSupportDialog);
  els.supportDialogPayPalBtn.addEventListener("click", () => openExternal("paypal_me").catch((error) => showToast(error.message)));
  els.supportDialogCloseBtn.addEventListener("click", closeSupportDialog);
  els.supportDialogCloseIconBtn.addEventListener("click", closeSupportDialog);
  els.supportDialog.addEventListener("click", (event) => {
    if (event.target === els.supportDialog) closeSupportDialog();
  });
  els.footerGithubBtn.addEventListener("click", () => openExternal("github_repository").catch((error) => showToast(error.message)));
  els.supportReminderOpenBtn.addEventListener("click", () => openSupportFromReminder().catch((error) => showToast(error.message)));
  els.supportReminderDismissBtn.addEventListener("click", () => updateSupportReminder("dismiss").catch((error) => showToast(error.message)));
  els.supportReminderDisableBtn.addEventListener("click", () => updateSupportReminder("disable").catch((error) => showToast(error.message)));
  els.supportReminderEnabledInput.addEventListener("change", () => {
    updateSupportReminder(els.supportReminderEnabledInput.checked ? "enable" : "disable").catch((error) => showToast(error.message));
  });
  els.shortcutIconInput.addEventListener("change", () => applyProfileIcon(els.shortcutIconInput.value));
  els.newProfileBtn.addEventListener("click", beginNewProfile);
  els.cancelNewProfileBtn.addEventListener("click", cancelNewProfile);
  els.profileSelect.addEventListener("change", () => {
    if (els.profileSelect.value === "__new") return;
    setProfileEditorMode(false);
    switchActiveProfile(els.profileSelect.value).catch((error) => showToast(error.message));
  });
  els.tabs.forEach((tab) => {
    tab.addEventListener("click", () => setActiveView(tab.dataset.view));
  });
  els.templateSelect.addEventListener("change", () => {
    const nextId = Number(els.templateSelect.value);
    if (state.templateDirty && !window.confirm("Abandonner les modifications non enregistrées ?")) {
      els.templateSelect.value = String(state.selectedTemplateId || "");
      return;
    }
    const selected = state.documentTemplates.find((item) => Number(item.id) === nextId);
    if (selected) showDocumentTemplate(selected);
  });
  [
    els.templateNameInput,
    els.templateDefaultInput,
    ...els.templateLabelInputs,
    els.templateBodySizeInput,
    els.templateTitleSizeInput,
    els.templateTableSizeInput,
    els.templateTextColorInput,
    els.templateTitleColorInput,
    els.templateHeaderColorInput,
    els.templateTotalColorInput,
    els.templateBorderColorInput,
    els.templateMarginTopInput,
    els.templateMarginBottomInput,
    els.templateMarginLeftInput,
    els.templateMarginRightInput,
    els.templateIdentityGapInput,
    els.templateTitleGapInput,
    els.templateRowHeightInput,
    els.templateMinimumRowsInput,
  ].forEach((input) => input.addEventListener("input", () => syncTemplateDraftFromForm(true)));
  els.templateBlocks.addEventListener("change", (event) => {
    const block = event.target.dataset.templateVisible;
    if (!block || !state.templateDraft) return;
    state.templateDraft.configuration.visible[block] = event.target.checked;
    setTemplateDirty(true);
    renderTemplatePreview();
  });
  els.templateBlocks.addEventListener("click", (event) => {
    const button = event.target.closest("[data-template-move]");
    if (button) moveTemplateBlock(button.dataset.templateMove, button.dataset.templateDirection);
  });
  els.templateNewBtn.addEventListener("click", () => createDocumentTemplate().catch((error) => showToast(error.message)));
  els.templateDuplicateBtn.addEventListener("click", () => duplicateDocumentTemplate().catch((error) => showToast(error.message)));
  els.templateDeleteBtn.addEventListener("click", () => deleteDocumentTemplate().catch((error) => showToast(error.message)));
  els.templateImportBtn.addEventListener("click", () => importDocumentTemplate().catch((error) => showToast(error.message)));
  els.templateResetBtn.addEventListener("click", () => resetDocumentTemplate().catch((error) => showToast(error.message)));
  els.templateSaveBtn.addEventListener("click", () => saveDocumentTemplate().catch((error) => showToast(error.message)));
  els.templateTestPdfBtn.addEventListener("click", () => generateTemplateTestPdf().catch((error) => showToast(error.message)));
  els.templateExportBtn.addEventListener("click", () => exportDocumentTemplate().catch((error) => showToast(error.message)));
  window.addEventListener("resize", () => {
    if (storedDisplayMode() === "auto") applyDisplayMode("auto", { persist: false });
    if (!els.templatesPanel.hidden && state.templateDraft) renderTemplatePreview();
  });
  els.clientsTopBtn.addEventListener("click", () => setActiveView("clients"));
  els.clientsShortcutBtn.addEventListener("click", () => setActiveView("clients"));
  els.refreshClientsBtn.addEventListener("click", refreshClients);
  els.clientForm.addEventListener("submit", saveClient);
  els.clientResetBtn.addEventListener("click", resetClientForm);
  els.reminderForm.addEventListener("submit", saveReminder);
  els.noteForm.addEventListener("submit", (event) => saveNote(event).catch((error) => showToast(error.message)));
  els.paymentForm.addEventListener("submit", (event) => savePayment(event).catch((error) => showToast(error.message)));
  els.notesList.addEventListener("click", (event) => {
    const id = event.target.dataset.deleteNote;
    if (id) api(`/api/notes/${id}`, { method: "DELETE" }).then(loadFollowup).catch((error) => showToast(error.message));
  });
  els.paymentsList.addEventListener("click", (event) => {
    const id = event.target.dataset.receivePayment;
    if (id) api(`/api/pending-payments/${id}`, { method: "PUT", body: JSON.stringify({ status: "recu" }) }).then(loadFollowup).catch((error) => showToast(error.message));
  });
  els.reminderResetBtn.addEventListener("click", resetReminderForm);
  els.planningTodayBtn.addEventListener("click", () => setActiveView("planning"));
  els.overviewApplyBtn.addEventListener("click", () => {
    loadOverview().catch((error) => showToast(error.message));
  });
  els.annualGranularity.addEventListener("change", () => {
    loadAnnualOverview().catch((error) => showToast(error.message));
  });
  els.comparisonDetails.addEventListener("toggle", () => {
    if (els.comparisonDetails.open && !state.overview) {
      loadOverview().catch((error) => showToast(error.message));
    }
  });
  els.interventionsBody.addEventListener("click", async (event) => {
    const editId = event.target.dataset.edit;
    const deleteId = event.target.dataset.delete;
    if (editId) {
      const row = state.interventions.find((item) => String(item.id) === String(editId));
      if (row) loadIntoForm(row);
    }
    if (deleteId) {
      await deleteIntervention(deleteId);
    }
  });
  els.clientsBody.addEventListener("click", (event) => {
    const clientName = event.target.dataset.editClient;
    const deleteClientName = event.target.dataset.deleteClient;
    if (clientName) {
      const client = state.clients.find((item) => item.name === clientName);
      if (client) loadIntoClientForm(client);
    }
    if (deleteClientName) {
      deleteClient(deleteClientName).catch((error) => showToast(error.message));
    }
  });
  document.addEventListener("click", (event) => {
    const stepperButton = event.target.closest("[data-step-target]");
    if (stepperButton) {
      const input = document.getElementById(stepperButton.dataset.stepTarget);
      const direction = Number(stepperButton.dataset.stepDirection);
      if (input && (direction === -1 || direction === 1)) {
        adjustSteppedNumber(input, direction);
      }
      return;
    }
    const button = event.target.closest("[data-complete-reminder]");
    if (button) {
      completeReminder(button.dataset.completeReminder, button.dataset.occurrenceId).catch((error) => showToast(error.message));
      return;
    }
    const editButton = event.target.closest("[data-edit-reminder]");
    if (editButton) {
      loadReminderIntoForm(editButton.dataset.editReminder);
      return;
    }
    const deleteButton = event.target.closest("[data-delete-reminder]");
    if (deleteButton) {
      deleteReminder(deleteButton.dataset.deleteReminder).catch((error) => showToast(error.message));
    }
  });
  els.clientInput.addEventListener("change", applySelectedClientDefaults);
}

function applySelectedClientDefaults() {
  const client = state.clients.find((item) => item.name === els.clientInput.value);
  if (!client) {
    els.rateInput.value = state.defaultRate.toFixed(2);
    return;
  }
  if (!els.locationInput.value) {
    els.locationInput.value = client.address || "";
  }
  if (client.hourly_rate_custom && Number(client.hourly_rate || 0) > 0) {
    els.rateInput.value = Number(client.hourly_rate).toFixed(2);
  } else {
    els.rateInput.value = state.defaultRate.toFixed(2);
  }
}

async function init() {
  applyDisplayMode(storedDisplayMode(), { persist: false });
  fillMonthSelect();
  bindEvents();
  const bootstrap = await api("/api/bootstrap");
  applyBootstrap(bootstrap);
  const appInfo = await api("/api/app-info");
  els.appVersion.textContent = appInfo.app_version || "inconnue";
  els.footerVersion.textContent = appInfo.app_version || "inconnue";
  await loadCommunity();
  setActiveView("interventions");
  await loadMonth();
  await loadPlanning();
  if (state.initialSetupRequired) {
    showSetupAssistant("first-run");
  }
  if ((state.reminders.notifications || []).length) {
    const count = state.reminders.notifications.length;
    showToast(`${count} rappel${count > 1 ? "s" : ""} à consulter dans le planning.`);
  }
}

init().catch((error) => showToast(error.message));
