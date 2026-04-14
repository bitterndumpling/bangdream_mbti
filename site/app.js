const APP_DATA = window.BANGDREAM_MBTI_DATA;

const STORAGE_KEYS = {
  lang: "bangdream_mbti_lang",
  answers: "bangdream_mbti_answers",
  currentIndex: "bangdream_mbti_current_index",
};

function resetPersistedQuizProgress() {
  localStorage.removeItem(STORAGE_KEYS.answers);
  localStorage.removeItem(STORAGE_KEYS.currentIndex);
}

resetPersistedQuizProgress();

const AXES = [
  ["EI", "E", "I"],
  ["SN", "S", "N"],
  ["FT", "F", "T"],
  ["JP", "J", "P"],
];

const RADAR_ORDER = ["E", "S", "T", "J", "I", "N", "F", "P"];
const BAND_ORDER = ["popipa", "afglo", "pasupare", "roselia", "hhw", "morfo", "ras", "mygo", "ave", "sumimi", "bangdream"];
const MATCH_TUNING = {
  userStretchPower: 0.7,
  characterShrink: 0.85,
  directionWeight: 0.7,
  extremenessWeight: 2.0,
};

const UI = {
  zh: {
    shortLang: "CN",
    htmlLang: "zh-CN",
    title: "BanG Dream! 角色性格拟合度测试",
    heroEyebrow: "Bang Dream Personality Match",
    heroTitle: "测出最像你的 BanG Dream! 角色",
    heroLead: "使用本地 OJTS 三语题库完成 48 道题目，看看你和哪几位 BanG Dream! 角色的八维轮廓最接近。",
    heroCount: "48 道本地题目",
    start: "开始测试",
    retake: "重新测试",
    questionLabel: "测试流程",
    questionTitle: "选择最符合你的选项",
    questionOrder: (index, total) => `第 ${index + 1} / ${total} 题`,
    progressText: (answered, total) => `已作答 ${answered} / ${total}`,
    agreementFormat: "同意度量表",
    bipolarFormat: "双端偏好",
    prev: "上一题",
    next: "下一题",
    resultsLabel: "测试结果",
    resultsTitle: "与你最接近的 3 位角色",
    userResultTitle: "你的八维结果",
    confidence: "结果稳定度",
    confidenceHigh: "高",
    confidenceMedium: "中",
    confidenceLow: "低",
    topPick: "最接近角色",
    matchScore: "拟合度",
    characterType: "角色类型",
    yourType: "你的类型",
    band: "所属",
    chartTitle: "八维雷达图",
    youLegend: "你的结果",
    characterLegend: "角色结果",
    rankLabel: (rank) => `Top ${rank}`,
    readmeButton: "Readme",
    readmeClose: "关闭",
    readmeLabel: "Readme",
    readmeTitle: "说明、感谢与免责声明",
    readmeThanksTitle: "参考与鸣谢",
    readmePrivacyTitle: "隐私保护说明",
    readmeDisclaimerTitle: "免责声明",
    readmeThanksIntro: "本页参考与素材来源：",
    privacyBody: "本页面完全在本地浏览器内运行，不会上传答案，不会收集、存储或发送任何用户资料、测试结果或设备信息。",
    disclaimerBody: "本项目代码由 AI 辅助生成，测试结果仅供图一乐和同人向娱乐体验使用，请不要将结果视为专业人格测评或官方角色设定结论。",
    copyright: APP_DATA.meta.copyrightNotice,
    axisMeaning: {
      E: "外向",
      S: "现实",
      T: "理性",
      J: "计划",
      I: "内向",
      N: "直觉",
      F: "情感",
      P: "灵活",
    },
    pairNames: {
      EI: "外向 / 内向",
      SN: "现实 / 直觉",
      FT: "情感 / 理性",
      JP: "计划 / 灵活",
    },
    agreementOptions: [
      ["非常不同意", "几乎完全不符合"],
      ["不同意", "更偏向不符合"],
      ["中立", "说不准 / 看情况"],
      ["同意", "比较符合"],
      ["非常同意", "几乎完全符合"],
    ],
    bipolarOptions: [
      ["更偏左侧", "明显靠近左边"],
      ["稍偏左侧", "有点偏左"],
      ["正中间", "两边都差不多"],
      ["稍偏右侧", "有点偏右"],
      ["更偏右侧", "明显靠近右边"],
    ],
  },
  en: {
    shortLang: "EN",
    htmlLang: "en",
    title: "BanG Dream! Character Match Test",
    heroEyebrow: "Bang Dream Personality Match",
    heroTitle: "Find the BanG Dream! characters closest to you",
    heroLead: "Answer 48 local OJTS questions and compare your eight-dimension profile with BanG Dream! characters.",
    heroCount: "48 local questions",
    start: "Start Test",
    retake: "Retake",
    questionLabel: "Question Flow",
    questionTitle: "Pick the option closest to you",
    questionOrder: (index, total) => `Question ${index + 1} / ${total}`,
    progressText: (answered, total) => `${answered} / ${total} answered`,
    agreementFormat: "Agreement Scale",
    bipolarFormat: "Bipolar Scale",
    prev: "Previous",
    next: "Next",
    resultsLabel: "Results",
    resultsTitle: "Your 3 closest character matches",
    userResultTitle: "Your eight-dimension result",
    confidence: "Result stability",
    confidenceHigh: "High",
    confidenceMedium: "Medium",
    confidenceLow: "Low",
    topPick: "Closest match",
    matchScore: "Match score",
    characterType: "Character type",
    yourType: "Your type",
    band: "Band / Unit",
    chartTitle: "Eight-dimension radar",
    youLegend: "Your result",
    characterLegend: "Character result",
    rankLabel: (rank) => `Top ${rank}`,
    readmeButton: "Readme",
    readmeClose: "Close",
    readmeLabel: "Readme",
    readmeTitle: "Notes, Credits, and Disclaimer",
    readmeThanksTitle: "Credits",
    readmePrivacyTitle: "Privacy",
    readmeDisclaimerTitle: "Disclaimer",
    readmeThanksIntro: "This page references the following projects and sources:",
    privacyBody: "This page runs entirely in your local browser. It does not upload answers, and it does not collect, store, or transmit any personal information or test results.",
    disclaimerBody: "The code for this page was generated with AI assistance. The test is meant for fun only and should not be treated as a professional personality assessment or official character canon.",
    copyright: APP_DATA.meta.copyrightNotice,
    axisMeaning: {
      E: "Extraversion",
      S: "Sensing",
      T: "Thinking",
      J: "Judging",
      I: "Introversion",
      N: "Intuition",
      F: "Feeling",
      P: "Perceiving",
    },
    pairNames: {
      EI: "Extraversion / Introversion",
      SN: "Sensing / Intuition",
      FT: "Feeling / Thinking",
      JP: "Judging / Perceiving",
    },
    agreementOptions: [
      ["Strongly disagree", "Almost completely unlike me"],
      ["Disagree", "Leans away from me"],
      ["Neutral", "Depends / not sure"],
      ["Agree", "Feels fairly like me"],
      ["Strongly agree", "Almost completely like me"],
    ],
    bipolarOptions: [
      ["Far left", "Clearly closer to the left side"],
      ["Slightly left", "A bit more left-leaning"],
      ["Middle", "About equally balanced"],
      ["Slightly right", "A bit more right-leaning"],
      ["Far right", "Clearly closer to the right side"],
    ],
  },
  ja: {
    shortLang: "JP",
    htmlLang: "ja",
    title: "BanG Dream! キャラクター適合度テスト",
    heroEyebrow: "Bang Dream Personality Match",
    heroTitle: "あなたに近い BanG Dream! キャラクターを見つける",
    heroLead: "ローカルの OJTS 48 問に答えて、あなたの八次元結果に近い BanG Dream! キャラクターを見つけます。",
    heroCount: "ローカル 48 問",
    start: "テスト開始",
    retake: "もう一度テスト",
    questionLabel: "テスト進行",
    questionTitle: "自分に近い選択肢を選んでください",
    questionOrder: (index, total) => `${index + 1} / ${total} 問`,
    progressText: (answered, total) => `${answered} / ${total} 回答済み`,
    agreementFormat: "同意スケール",
    bipolarFormat: "両極スケール",
    prev: "前へ",
    next: "次へ",
    resultsLabel: "結果",
    resultsTitle: "あなたに近い 3 人のキャラクター",
    userResultTitle: "あなたの八次元結果",
    confidence: "結果の安定度",
    confidenceHigh: "高",
    confidenceMedium: "中",
    confidenceLow: "低",
    topPick: "最も近いキャラ",
    matchScore: "適合度",
    characterType: "キャラタイプ",
    yourType: "あなたのタイプ",
    band: "所属",
    chartTitle: "八次元レーダー",
    youLegend: "あなたの結果",
    characterLegend: "キャラクター結果",
    rankLabel: (rank) => `Top ${rank}`,
    readmeButton: "Readme",
    readmeClose: "閉じる",
    readmeLabel: "Readme",
    readmeTitle: "説明・謝辞・免責事項",
    readmeThanksTitle: "参考と謝辞",
    readmePrivacyTitle: "プライバシー",
    readmeDisclaimerTitle: "免責事項",
    readmeThanksIntro: "参考にした内容と素材元：",
    privacyBody: "このページは完全にローカルブラウザ内で動作します。回答内容や結果、個人情報を送信・収集・保存することはありません。",
    disclaimerBody: "このページのコードは AI 支援で作成されています。結果はあくまで娯楽向けの参考表示であり、専門的な性格診断や公式設定の断定ではありません。",
    copyright: APP_DATA.meta.copyrightNotice,
    axisMeaning: {
      E: "外向",
      S: "感覚",
      T: "思考",
      J: "判断",
      I: "内向",
      N: "直観",
      F: "感情",
      P: "知覚",
    },
    pairNames: {
      EI: "外向 / 内向",
      SN: "感覚 / 直観",
      FT: "感情 / 思考",
      JP: "判断 / 知覚",
    },
    agreementOptions: [
      ["全くそう思わない", "ほとんど当てはまらない"],
      ["あまりそう思わない", "やや違う"],
      ["どちらでもない", "状況による"],
      ["そう思う", "かなり当てはまる"],
      ["とてもそう思う", "ほぼその通り"],
    ],
    bipolarOptions: [
      ["かなり左寄り", "左側に明確に近い"],
      ["やや左寄り", "少し左に寄る"],
      ["真ん中", "ほぼ半々"],
      ["やや右寄り", "少し右に寄る"],
      ["かなり右寄り", "右側に明確に近い"],
    ],
  },
};

const elements = {
  langSwitcher: document.getElementById("lang-switcher"),
  hero: document.getElementById("hero"),
  quizSection: document.getElementById("quiz-section"),
  resultsSection: document.getElementById("results-section"),
  heroEyebrow: document.getElementById("hero-eyebrow"),
  heroTitle: document.getElementById("hero-title"),
  heroLead: document.getElementById("hero-lead"),
  heroPillCount: document.getElementById("hero-pill-count"),
  startBtn: document.getElementById("start-btn"),
  questionLabel: document.getElementById("question-label"),
  questionTitle: document.getElementById("question-title"),
  progressText: document.getElementById("progress-text"),
  progressFill: document.getElementById("progress-fill"),
  questionOrder: document.getElementById("question-order"),
  questionFormat: document.getElementById("question-format"),
  questionText: document.getElementById("question-text"),
  questionHints: document.getElementById("question-hints"),
  bipolarScale: document.getElementById("bipolar-scale"),
  bipolarLeft: document.getElementById("bipolar-left"),
  bipolarRight: document.getElementById("bipolar-right"),
  answerList: document.getElementById("answer-list"),
  prevBtn: document.getElementById("prev-btn"),
  nextBtn: document.getElementById("next-btn"),
  resultsLabel: document.getElementById("results-label"),
  resultsTitle: document.getElementById("results-title"),
  retakeBtnBottom: document.getElementById("retake-btn-bottom"),
  userResult: document.getElementById("user-result"),
  topMatches: document.getElementById("top-matches"),
  readmeBtn: document.getElementById("readme-btn"),
  galleryBtn: document.getElementById("gallery-btn"),
  gallerySection: document.getElementById("gallery-section"),
  galleryLabel: document.getElementById("gallery-label"),
  galleryTitle: document.getElementById("gallery-title"),
  galleryGroups: document.getElementById("gallery-groups"),
  readmeModal: document.getElementById("readme-modal"),
  readmeBackdrop: document.getElementById("readme-backdrop"),
  readmeContent: document.getElementById("readme-content"),
  readmeClose: document.getElementById("readme-close"),
  hoverTooltip: document.getElementById("hover-tooltip"),
  brand: document.querySelector(".brand"),
};

const state = {
  lang: loadLanguage(),
  answers: loadAnswers(),
  currentIndex: loadCurrentIndex(),
  charts: [],
  view: "home",
  readmeOpen: false,
};

function getQuestions(lang = state.lang) {
  return APP_DATA.questions[lang].questions;
}

function loadLanguage() {
  const saved = localStorage.getItem(STORAGE_KEYS.lang);
  return UI[saved] ? saved : "zh";
}

function loadAnswers() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEYS.answers) || "[]");
    if (Array.isArray(saved) && saved.length === getQuestions("zh").length) {
      return saved.map((value) => (Number.isInteger(value) && value >= 1 && value <= 5 ? value : null));
    }
  } catch (error) {
    console.warn("Failed to read answers", error);
  }
  return Array.from({ length: getQuestions("zh").length }, () => null);
}

function loadCurrentIndex() {
  const raw = Number.parseInt(localStorage.getItem(STORAGE_KEYS.currentIndex), 10);
  const total = getQuestions("zh").length;
  return Number.isFinite(raw) ? clamp(raw, 0, total - 1) : 0;
}

function detectInitialView() {
  if (state.answers.every((item) => Number.isInteger(item))) return "results";
  if (state.answers.some((item) => Number.isInteger(item))) return "quiz";
  return "home";
}

function persistState() {
  localStorage.setItem(STORAGE_KEYS.lang, state.lang);
  localStorage.setItem(STORAGE_KEYS.answers, JSON.stringify(state.answers));
  localStorage.setItem(STORAGE_KEYS.currentIndex, String(state.currentIndex));
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function getAnsweredCount() {
  return state.answers.filter((answer) => Number.isInteger(answer)).length;
}

function hasCurrentAnswer() {
  return Number.isInteger(state.answers[state.currentIndex]);
}

function isComplete() {
  return getAnsweredCount() === state.answers.length;
}

function confidenceLabel(confidence) {
  const t = UI[state.lang];
  if (confidence >= 45) return t.confidenceHigh;
  if (confidence >= 22) return t.confidenceMedium;
  return t.confidenceLow;
}

function getSignedAxisValue(percentages, leftPole, rightPole) {
  return (percentages[leftPole] || 0) - (percentages[rightPole] || 0);
}

function getSignedVector(percentages) {
  return AXES.map(([, leftPole, rightPole]) => getSignedAxisValue(percentages, leftPole, rightPole) / 100);
}

function transformUserVector(vector) {
  return vector.map((value) => Math.sign(value) * Math.pow(Math.abs(value), MATCH_TUNING.userStretchPower));
}

function transformCharacterVector(vector) {
  return vector.map((value) => value * MATCH_TUNING.characterShrink);
}

function getVectorNorm(vector) {
  return Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
}

function getCosineSimilarity(left, right) {
  const leftNorm = getVectorNorm(left);
  const rightNorm = getVectorNorm(right);
  if (!leftNorm || !rightNorm) return 0;
  const dot = left.reduce((sum, value, index) => sum + value * right[index], 0);
  return clamp(dot / (leftNorm * rightNorm), -1, 1);
}

function getWeightedAxisCloseness(userVector, characterVector) {
  const weighted = userVector.reduce(
    (acc, value, index) => {
      const characterValue = characterVector[index];
      const weight = 1 + Math.max(Math.abs(value), Math.abs(characterValue)) * MATCH_TUNING.extremenessWeight;
      const closeness = clamp(1 - Math.abs(value - characterValue) / 2, 0, 1);
      acc.score += closeness * weight;
      acc.weight += weight;
      return acc;
    },
    { score: 0, weight: 0 }
  );

  return weighted.weight ? weighted.score / weighted.weight : 0;
}

function computeUserResult() {
  if (!isComplete()) return null;
  const scores = { E: 0, I: 0, S: 0, N: 0, F: 0, T: 0, J: 0, P: 0 };
  const questions = getQuestions("en");

  questions.forEach((question, index) => {
    const answer = state.answers[index];
    if (!Number.isInteger(answer)) return;
    if (question.format === "agreement") {
      const support = answer - 1;
      question.poles.forEach((pole) => {
        scores[pole] += support;
      });
    } else {
      scores[question.left_pole] += 5 - answer;
      scores[question.right_pole] += answer - 1;
    }
  });

  const percentages = {};
  const pairMargins = {};
  const type = [];

  AXES.forEach(([axis, left, right]) => {
    const total = scores[left] + scores[right];
    const leftPct = total ? clamp(Math.round((scores[left] / total) * 10000) / 100, 1, 99) : 50;
    const rightPct = Math.round((100 - leftPct) * 100) / 100;
    const winner = leftPct >= rightPct ? left : right;
    percentages[left] = leftPct;
    percentages[right] = rightPct;
    pairMargins[axis] = {
      winner,
      loser: winner === left ? right : left,
      margin: Math.round(Math.abs(leftPct - rightPct) * 100) / 100,
    };
    type.push(winner);
  });

  const confidence = Math.round(
    (Object.values(pairMargins).reduce((sum, item) => sum + item.margin, 0) / AXES.length) * 100
  ) / 100;

  return {
    scores,
    percentages,
    pairMargins,
    confidence,
    type: type.join(""),
  };
}

function computeMatches(userPercentages) {
  const userVector = transformUserVector(getSignedVector(userPercentages));

  return APP_DATA.characters
    .map((character) => {
      const characterVector = transformCharacterVector(getSignedVector(character.percentages));
      const directionScore = (getCosineSimilarity(userVector, characterVector) + 1) / 2;
      const axisCloseness = getWeightedAxisCloseness(userVector, characterVector);
      const compositeScore =
        directionScore * MATCH_TUNING.directionWeight +
        axisCloseness * (1 - MATCH_TUNING.directionWeight);
      const similarity = Math.round(clamp(compositeScore, 0, 1) * 10000) / 100;

      return {
        ...character,
        similarity: clamp(similarity, 0, 100),
        matchScore: compositeScore,
        directionScore,
        axisCloseness,
      };
    })
    .sort(
      (a, b) =>
        b.matchScore - a.matchScore ||
        b.directionScore - a.directionScore ||
        b.axisCloseness - a.axisCloseness ||
        a.id.localeCompare(b.id)
    );
}

function getLocalizedCharacterName(character, lang = state.lang) {
  return character.names?.[lang] || character.fullName || character.englishName || character.displayName || "";
}

function getLocalizedCharacterDescription(character, lang = state.lang) {
  return character.descriptions?.[lang] || character.description || "";
}

function getSecondaryCharacterNames(character, lang = state.lang) {
  const primary = getLocalizedCharacterName(character, lang);
  const seen = new Set([primary]);
  return ["zh", "en", "ja"]
    .filter((item) => item !== lang)
    .map((item) => character.names?.[item])
    .filter((name) => name && !seen.has(name) && seen.add(name));
}

function getLocalizedBandName(character, lang = state.lang) {
  if (character.bandKey === "bangdream") {
    if (lang === "zh") return "其他角色";
    if (lang === "ja") return "その他キャラクター";
    return "Other Characters";
  }
  return character.bandName;
}

function createElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function moveHoverTooltip(clientX, clientY) {
  const tooltip = elements.hoverTooltip;
  if (tooltip.hidden) return;

  const offset = 14;
  const rect = tooltip.getBoundingClientRect();
  const maxLeft = window.innerWidth - rect.width - 12;
  const maxTop = window.innerHeight - rect.height - 12;
  const left = Math.min(clientX + offset, Math.max(12, maxLeft));
  const top = Math.min(clientY + offset, Math.max(12, maxTop));

  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top}px`;
}

function showHoverTooltip(text, clientX, clientY) {
  if (!text) return;
  elements.hoverTooltip.textContent = text;
  elements.hoverTooltip.hidden = false;
  moveHoverTooltip(clientX, clientY);
}

function hideHoverTooltip() {
  elements.hoverTooltip.hidden = true;
}

function attachHoverTooltip(node, text) {
  node.addEventListener("mouseenter", (event) => {
    showHoverTooltip(text, event.clientX, event.clientY);
  });
  node.addEventListener("mousemove", (event) => {
    moveHoverTooltip(event.clientX, event.clientY);
  });
  node.addEventListener("mouseleave", hideHoverTooltip);
}

function getGalleryButtonText() {
  return state.lang === "zh" ? "角色图鉴" : state.lang === "ja" ? "キャラ一覧" : "Characters";
}

function getGalleryLabelText() {
  return state.lang === "zh" ? "角色图鉴" : state.lang === "ja" ? "キャラ一覧" : "Character Gallery";
}

function getGalleryTitleText() {
  return state.lang === "zh"
    ? "按乐队查看全部角色"
    : state.lang === "ja"
      ? "バンド別に全キャラクターを見る"
      : "Browse Every Character by Band";
}

function getCharacterCountText(count) {
  return state.lang === "zh"
    ? `${count} 位角色`
    : state.lang === "ja"
      ? `${count} 人`
      : `${count} characters`;
}

function renderLanguageSwitcher() {
  elements.langSwitcher.innerHTML = "";
  Object.entries(UI).forEach(([lang, meta]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = meta.shortLang;
    button.className = lang === state.lang ? "is-active" : "";
    button.addEventListener("click", () => {
      state.lang = lang;
      persistState();
      render();
    });
    elements.langSwitcher.appendChild(button);
  });
}

function renderHero() {
  const t = UI[state.lang];
  document.documentElement.lang = t.htmlLang;
  document.title = t.title;
  elements.heroEyebrow.textContent = t.heroEyebrow;
  elements.heroTitle.textContent = t.heroTitle;
  elements.heroLead.textContent = t.heroLead;
  elements.heroPillCount.textContent = t.heroCount;
  elements.startBtn.textContent = t.start;
  elements.galleryBtn.textContent = getGalleryButtonText();
}

function renderQuestion() {
  const t = UI[state.lang];
  const questions = getQuestions(state.lang);
  const question = questions[state.currentIndex];
  const answer = state.answers[state.currentIndex];
  const questionLabelText =
    state.lang === "zh" ? "答题流程" :
    state.lang === "ja" ? "回答フロー" :
    "Answer Flow";

  elements.questionLabel.textContent = questionLabelText;
  elements.questionTitle.textContent = t.questionTitle;
  elements.progressText.textContent = t.progressText(getAnsweredCount(), questions.length);
  elements.progressFill.style.width = `${(getAnsweredCount() / questions.length) * 100}%`;
  elements.questionOrder.textContent = t.questionOrder(state.currentIndex, questions.length);
  elements.questionFormat.textContent = question.format === "agreement" ? t.agreementFormat : t.bipolarFormat;
  elements.questionText.textContent = question.format === "agreement" ? question.text : `${question.left_text} <-> ${question.right_text}`;

  elements.questionHints.innerHTML = "";
  elements.questionHints.hidden = true;

  if (question.format === "bipolar") {
    elements.bipolarScale.hidden = false;
    elements.bipolarLeft.textContent = question.left_text;
    elements.bipolarRight.textContent = question.right_text;
  } else {
    elements.bipolarScale.hidden = true;
  }

  const options = question.format === "agreement"
    ? t.agreementOptions.map(([title, subtitle], index) => ({ title, subtitle, value: index + 1 })).reverse()
    : t.bipolarOptions.map(([title, subtitle], index) => ({ title, subtitle, value: index + 1 }));
  elements.answerList.className = question.format === "bipolar" ? "answer-list is-bipolar" : "answer-list";
  elements.answerList.innerHTML = "";

  options.forEach(({ title, subtitle, value }) => {
    const button = createElement("button", `answer-btn${question.format === "bipolar" ? " is-bipolar" : ""}`);
    button.type = "button";
    if (answer === value) button.classList.add("is-selected");
    button.append(createElement("strong", null, title), createElement("span", null, subtitle));
    button.addEventListener("click", () => {
      state.answers[state.currentIndex] = value;
      persistState();
      render();
      window.clearTimeout(button._advanceTimer);
      button._advanceTimer = window.setTimeout(() => {
        if (state.currentIndex < state.answers.length - 1) {
          state.currentIndex += 1;
          persistState();
          render();
        } else if (isComplete()) {
          showResults();
        }
      }, 120);
    });
    elements.answerList.appendChild(button);
  });

  elements.prevBtn.textContent = t.prev;
  elements.nextBtn.textContent = t.next;
  elements.prevBtn.disabled = state.currentIndex === 0;
  elements.nextBtn.disabled = state.currentIndex === state.answers.length - 1 || !hasCurrentAnswer();
}

function renderUserResult(userResult, matches) {
  const t = UI[state.lang];
  elements.resultsLabel.textContent = t.resultsLabel;
  elements.resultsTitle.textContent = t.resultsTitle;
  elements.retakeBtnBottom.textContent = t.retake;

  if (!userResult) {
    elements.userResult.innerHTML = "";
    elements.topMatches.innerHTML = "";
    state.charts = [];
    return;
  }

  elements.userResult.innerHTML = "";
  const head = createElement("div", "user-result-head");
  const left = document.createElement("div");
  left.append(
    createElement("p", "section-label", t.userResultTitle),
    createElement("h3", "result-type", userResult.type)
  );

  const right = createElement("div", "result-summary");
  right.append(
    createElement("span", "stat-chip", `${t.confidence}: ${confidenceLabel(userResult.confidence)} (${userResult.confidence.toFixed(1)})`),
    createElement("span", "stat-chip", `${t.topPick}: ${getLocalizedCharacterName(matches[0])}`),
    createElement("span", "stat-chip", `${t.matchScore}: ${matches[0].similarity.toFixed(2)}%`)
  );
  head.append(left, right);
  elements.userResult.appendChild(head);

  const axisBars = createElement("div", "axis-bars");
  AXES.forEach(([axis, leftPole, rightPole]) => {
    const wrapper = createElement("div", "axis-bar");
    const header = document.createElement("header");
    header.append(
      createElement("span", null, t.pairNames[axis]),
      createElement("strong", null, `${userResult.percentages[leftPole].toFixed(2)} / ${userResult.percentages[rightPole].toFixed(2)}`)
    );
    const track = createElement("div", "bar-track");
    const fill = createElement("div", "bar-fill");
    fill.style.width = `${userResult.percentages[leftPole]}%`;
    track.appendChild(fill);
    wrapper.append(header, track);
    axisBars.appendChild(wrapper);
  });
  elements.userResult.appendChild(axisBars);
}

function renderMatchCards(userResult, matches) {
  const t = UI[state.lang];
  elements.topMatches.innerHTML = "";

  matches.slice(0, 3).forEach((character, index) => {
    const localizedName = getLocalizedCharacterName(character);
    const secondaryNames = getSecondaryCharacterNames(character);
    const localizedDescription = getLocalizedCharacterDescription(character);
    const localizedBandName = getLocalizedBandName(character);
    const card = createElement("article", "match-card");
    card.style.setProperty("--card-color", character.color);

    const visual = createElement("div", "match-visual");
    visual.appendChild(createElement("span", "rank-badge", t.rankLabel(index + 1)));
    const portrait = document.createElement("img");
    portrait.className = "portrait";
    portrait.src = character.portraitUrl;
    portrait.alt = localizedName;
    visual.appendChild(portrait);

    const body = createElement("div", "match-body");
    const topline = createElement("div", "match-topline");
    const titleWrap = document.createElement("div");
    titleWrap.append(
      createElement("h3", "match-name", localizedName),
      createElement("div", "match-sub", `${character.englishName} · ${t.characterType}: ${character.type}`)
    );
    topline.append(titleWrap, createElement("span", "fit-chip", `${t.matchScore}: ${character.similarity.toFixed(2)}%`));
    titleWrap.querySelector(".match-name").textContent = localizedName;
    titleWrap.querySelector(".match-sub").textContent = `${secondaryNames.join(" / ")}${secondaryNames.length ? " · " : ""}${t.characterType}: ${character.type}`;

    titleWrap.querySelector(".match-sub").textContent = `${secondaryNames.join(" / ")}${secondaryNames.length ? " / " : ""}${t.characterType}: ${character.type}`;

    const bands = createElement("div", "match-bands");
    const bandChip = createElement("div", "band-chip");
    bandChip.title = `${t.band}: ${localizedBandName}`;
    const logo = document.createElement("img");
    logo.src = character.bandLogoUrl;
    logo.alt = localizedBandName;
    bandChip.append(logo, createElement("span", null, localizedBandName));
    bands.appendChild(bandChip);

    const stats = createElement("div", "match-stats");
    stats.append(
      createElement("span", "stat-chip", `${t.yourType}: ${userResult.type}`),
      createElement("span", "stat-chip", `${t.characterType}: ${character.type}`),
      createElement("span", "stat-chip", `${t.band}: ${localizedBandName}`)
    );

    const description = createElement("p", "result-description", localizedDescription);
    const chartCard = createElement("div", "chart-card");
    chartCard.appendChild(createElement("div", "mini-label", t.chartTitle));
    const legend = createElement("div", "chart-legend");
    const userLegend = document.createElement("span");
    userLegend.innerHTML = `<span class="legend-swatch" style="background:#7b7b7b;"></span> ${t.youLegend}`;
    const charLegend = document.createElement("span");
    charLegend.innerHTML = `<span class="legend-swatch" style="background:${character.color};"></span> ${t.characterLegend}`;
    legend.append(userLegend, charLegend);
    chartCard.appendChild(legend);
    const canvas = document.createElement("canvas");
    canvas.className = "radar-canvas";
    chartCard.appendChild(canvas);
    state.charts.push({ canvas, userPercentages: userResult.percentages, character });

    body.append(topline, bands, stats, description, chartCard);
    card.append(visual, body);
    elements.topMatches.appendChild(card);
  });

  rerenderCharts();
}

function renderGallery() {
  const t = UI[state.lang];
  elements.galleryLabel.textContent = getGalleryLabelText();
  elements.galleryTitle.textContent = getGalleryTitleText();
  elements.galleryGroups.innerHTML = "";

  BAND_ORDER.forEach((bandKey) => {
    const characters = APP_DATA.characters
      .filter((character) => character.bandKey === bandKey)
      .sort((a, b) => getLocalizedCharacterName(a).localeCompare(getLocalizedCharacterName(b), UI[state.lang].htmlLang));

    if (!characters.length) return;
    const localizedBandName = getLocalizedBandName(characters[0]);

    const group = createElement("section", "gallery-group");
    const header = createElement("div", "gallery-group-head");
    const titleWrap = document.createElement("div");
    const bandTitle = createElement("h3", "gallery-band-title", localizedBandName);
    const meta = createElement("span", "gallery-band-count", getCharacterCountText(characters.length));
    titleWrap.append(bandTitle);

    const chip = createElement("div", "band-chip");
    chip.title = localizedBandName;
    const logo = document.createElement("img");
    logo.src = characters[0].bandLogoUrl;
    logo.alt = localizedBandName;
    chip.append(logo, createElement("span", null, localizedBandName));

    header.append(titleWrap, createElement("div", "gallery-band-meta"));
    header.lastChild.append(meta, chip);

    const grid = createElement("div", "gallery-grid");

    characters.forEach((character) => {
      const localizedName = getLocalizedCharacterName(character);
      const secondaryNames = getSecondaryCharacterNames(character);
      const localizedBandNameForCard = getLocalizedBandName(character);
      const card = createElement("article", "gallery-item");
      card.style.setProperty("--card-color", character.color);

      const visual = createElement("div", "gallery-visual");
      const portrait = document.createElement("img");
      portrait.src = character.portraitUrl;
      portrait.alt = localizedName;
      visual.appendChild(portrait);

      const body = createElement("div", "gallery-body");
      body.append(
        createElement("h4", "gallery-name", localizedName),
        createElement("div", "gallery-sub", secondaryNames.join(" / ")),
      );

      const metaRow = createElement("div", "gallery-meta");
      metaRow.append(
        createElement("span", "stat-chip", `${UI[state.lang].characterType}: ${character.type}`),
        createElement("span", "stat-chip", localizedBandNameForCard),
      );

      const description = createElement("p", "gallery-description", getLocalizedCharacterDescription(character));
      attachHoverTooltip(description, getLocalizedCharacterDescription(character));
      const chartCard = createElement("div", "chart-card gallery-chart-card");
      chartCard.appendChild(createElement("div", "mini-label", t.chartTitle));
      const canvas = document.createElement("canvas");
      canvas.className = "radar-canvas gallery-radar-canvas";
      canvas.dataset.minSize = "180";
      canvas.dataset.maxSize = "240";
      chartCard.appendChild(canvas);
      state.charts.push({ canvas, character });

      body.append(metaRow, description, chartCard);

      card.append(visual, body);
      grid.appendChild(card);
    });

    group.append(header, grid);
    elements.galleryGroups.appendChild(group);
  });
}

function drawRadar(canvas, userPercentages, character) {
  const t = UI[state.lang];
  const labels = RADAR_ORDER.map((pole) => t.axisMeaning[pole]);
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  const minSize = Number.parseFloat(canvas.dataset.minSize || "260");
  const maxSize = Number.parseFloat(canvas.dataset.maxSize || "420");
  const size = Math.max(minSize, Math.min(rect.width || maxSize, maxSize));
  canvas.width = size * dpr;
  canvas.height = size * dpr;

  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, size, size);

  const center = size / 2;
  const radius = size * 0.31;
  ctx.strokeStyle = "rgba(105, 79, 55, 0.12)";
  ctx.lineWidth = 1;

  for (let ring = 1; ring <= 5; ring += 1) {
    ctx.beginPath();
    RADAR_ORDER.forEach((_, index) => {
      const point = getRadarPoint(index, ring / 5, center, radius);
      if (index === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.closePath();
    ctx.stroke();
  }

  RADAR_ORDER.forEach((_, index) => {
    const outer = getRadarPoint(index, 1, center, radius);
    ctx.beginPath();
    ctx.moveTo(center, center);
    ctx.lineTo(outer.x, outer.y);
    ctx.stroke();
  });

  drawPolygon(ctx, center, radius, character.percentages, hexToRgba(character.color, 0.95), hexToRgba(character.color, 0.2));
  if (userPercentages) {
    drawPolygon(ctx, center, radius, userPercentages, "rgba(115, 115, 115, 0.96)", "rgba(115, 115, 115, 0.18)");
  }

  ctx.fillStyle = "rgba(57, 43, 31, 0.88)";
  ctx.font = `${size < 220 ? 9 : size < 320 ? 11 : 12}px sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  labels.forEach((label, index) => {
    const point = getRadarPoint(index, 1.15, center, radius);
    ctx.fillText(label, point.x, point.y);
  });
}

function drawPolygon(ctx, center, radius, percentages, stroke, fill) {
  ctx.beginPath();
  RADAR_ORDER.forEach((pole, index) => {
    const point = getRadarPoint(index, percentages[pole] / 100, center, radius);
    if (index === 0) ctx.moveTo(point.x, point.y);
    else ctx.lineTo(point.x, point.y);
  });
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = 2.5;
  ctx.fill();
  ctx.stroke();
}

function getRadarPoint(index, ratio, center, radius) {
  const angle = (-Math.PI / 2) + (Math.PI * 2 * index) / RADAR_ORDER.length;
  return {
    x: center + Math.cos(angle) * radius * ratio,
    y: center + Math.sin(angle) * radius * ratio,
  };
}

function hexToRgba(hex, alpha) {
  const normalized = hex.replace("#", "");
  const r = Number.parseInt(normalized.slice(0, 2), 16);
  const g = Number.parseInt(normalized.slice(2, 4), 16);
  const b = Number.parseInt(normalized.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function rerenderCharts() {
  state.charts.forEach(({ canvas, userPercentages = null, character }) => {
    drawRadar(canvas, userPercentages, character);
  });
}

function renderReadme() {
  const t = UI[state.lang];
  elements.readmeBtn.textContent = t.readmeButton;
  elements.readmeClose.textContent = t.readmeClose;
  elements.readmeContent.innerHTML = `
    <section class="readme-block">
      <h3>${t.readmeDisclaimerTitle}</h3>
      <p>${t.disclaimerBody}</p>
    </section>
    <section class="readme-block">
      <h3>${t.readmePrivacyTitle}</h3>
      <p>${t.privacyBody}</p>
    </section>
    <section class="readme-block">
      <h3>${t.readmeThanksTitle}</h3>
      <p>${t.readmeThanksIntro}</p>
      <ul class="readme-link-list">
        <li><a href="${APP_DATA.meta.referenceSite}" target="_blank" rel="noreferrer">jcver.github.io/Gakumas-idolmaster-MBTI-test</a></li>
        <li><a href="${APP_DATA.meta.ojtsSource}" target="_blank" rel="noreferrer">OpenPsychometrics OJTS v2.1</a></li>
        <li><a href="${APP_DATA.meta.fandomWiki}" target="_blank" rel="noreferrer">BanG Dream! Wikia</a></li>
        <li><a href="https://www.personality-database.com" target="_blank" rel="noreferrer">Personality Database</a></li>
        <li><a href="https://bestdori.com" target="_blank" rel="noreferrer">Bestdori!</a></li>
      </ul>
      <p class="copyright-note">${t.copyright}</p>
    </section>
  `;
  elements.readmeModal.hidden = !state.readmeOpen;
}

function renderView(userResult) {
  if (state.view === "results" && !userResult) {
    state.view = getAnsweredCount() > 0 ? "quiz" : "home";
  }
  elements.hero.hidden = state.view !== "home";
  elements.quizSection.hidden = state.view !== "quiz";
  elements.resultsSection.hidden = state.view !== "results" || !userResult;
  elements.gallerySection.hidden = state.view !== "gallery";
}

function render() {
  const userResult = computeUserResult();
  const matches = userResult ? computeMatches(userResult.percentages) : [];
  state.charts = [];
  renderLanguageSwitcher();
  renderHero();
  renderQuestion();
  renderUserResult(userResult, matches);
  if (userResult) renderMatchCards(userResult, matches);
  renderGallery();
  renderReadme();
  renderView(userResult);
  rerenderCharts();
}

function showQuiz() {
  state.view = "quiz";
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showResults() {
  if (!isComplete()) return;
  state.view = "results";
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetQuiz() {
  state.answers = Array.from({ length: state.answers.length }, () => null);
  state.currentIndex = 0;
  state.view = "home";
  persistState();
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showGallery() {
  state.view = "gallery";
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

elements.startBtn.addEventListener("click", showQuiz);
elements.galleryBtn.addEventListener("click", showGallery);
elements.retakeBtnBottom.addEventListener("click", resetQuiz);
elements.prevBtn.addEventListener("click", () => {
  state.currentIndex = clamp(state.currentIndex - 1, 0, state.answers.length - 1);
  persistState();
  render();
});
elements.nextBtn.addEventListener("click", () => {
  if (!hasCurrentAnswer()) return;
  state.currentIndex = clamp(state.currentIndex + 1, 0, state.answers.length - 1);
  persistState();
  render();
});
elements.readmeBtn.addEventListener("click", () => {
  state.readmeOpen = true;
  renderReadme();
});
elements.readmeClose.addEventListener("click", () => {
  state.readmeOpen = false;
  renderReadme();
});
elements.readmeBackdrop.addEventListener("click", () => {
  state.readmeOpen = false;
  renderReadme();
});
elements.brand.addEventListener("click", (event) => {
  event.preventDefault();
  state.view = "home";
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && state.readmeOpen) {
    state.readmeOpen = false;
    renderReadme();
  }
  if (event.key === "Escape" && !elements.hoverTooltip.hidden) {
    hideHoverTooltip();
  }
});

window.addEventListener("resize", debounce(rerenderCharts, 100));
window.addEventListener("scroll", hideHoverTooltip, { passive: true });

function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => fn(...args), delay);
  };
}

state.view = detectInitialView();
render();
