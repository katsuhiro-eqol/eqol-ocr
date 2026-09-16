const LP_CSS = `
:root {
  --lp-bg:          #EFF4FA;
  --lp-surface:     #FFFFFF;
  --lp-surface-2:   #E4EDF7;
  --lp-border:      #C8D8EA;
  --lp-text:        #182535;
  --lp-text-2:      #4E6A84;
  --lp-text-3:      #8AAABF;
  --lp-accent:      #0052A8;
  --lp-accent-h:    #003F86;
  --lp-accent-2:    #007A57;
  --lp-accent-lt:   #E6F0FF;
  --lp-accent-2-lt: #E3F4EE;
  --lp-rule:        rgba(0,82,168,.065);
  --lp-sh:          0 2px 12px rgba(24,37,53,.08);
  --lp-sh-lg:       0 8px 32px rgba(24,37,53,.13);
  --lp-r:           8px;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --lp-bg:          #0C1825;
    --lp-surface:     #132030;
    --lp-surface-2:   #1C2E42;
    --lp-border:      #253E58;
    --lp-text:        #D5E8FF;
    --lp-text-2:      #7AAAC8;
    --lp-text-3:      #426480;
    --lp-accent:      #4FA0FF;
    --lp-accent-h:    #6EB5FF;
    --lp-accent-2:    #2DBD8A;
    --lp-accent-lt:   #142A46;
    --lp-accent-2-lt: #113028;
    --lp-rule:        rgba(79,160,255,.065);
    --lp-sh:          0 2px 12px rgba(0,0,0,.32);
    --lp-sh-lg:       0 8px 32px rgba(0,0,0,.44);
  }
}
:root[data-theme="dark"] {
  --lp-bg:          #0C1825;
  --lp-surface:     #132030;
  --lp-surface-2:   #1C2E42;
  --lp-border:      #253E58;
  --lp-text:        #D5E8FF;
  --lp-text-2:      #7AAAC8;
  --lp-text-3:      #426480;
  --lp-accent:      #4FA0FF;
  --lp-accent-h:    #6EB5FF;
  --lp-accent-2:    #2DBD8A;
  --lp-accent-lt:   #142A46;
  --lp-accent-2-lt: #113028;
  --lp-rule:        rgba(79,160,255,.065);
  --lp-sh:          0 2px 12px rgba(0,0,0,.32);
  --lp-sh-lg:       0 8px 32px rgba(0,0,0,.44);
}

.lp { background: var(--lp-bg); color: var(--lp-text); font-family: 'Noto Sans JP','Hiragino Kaku Gothic ProN','Meiryo',sans-serif; font-size: 16px; line-height: 1.75; -webkit-font-smoothing: antialiased; min-height: 100vh; }
.lp *, .lp *::before, .lp *::after { box-sizing: border-box; }
.lp p { max-width: 62ch; }
.lp h1,.lp h2,.lp h3 { font-family:'Noto Serif JP','Hiragino Mincho ProN',serif; font-weight:700; text-wrap:balance; line-height:1.35; }
.lp h1 { font-size: clamp(1.875rem,4vw,2.875rem); }
.lp h2 { font-size: clamp(1.375rem,3vw,1.875rem); }
.lp a { color: inherit; }

.lp .lp-container { max-width:1072px; margin-inline:auto; padding-inline:24px; }

/* NAV */
.lp nav { background:var(--lp-surface); border-bottom:1px solid var(--lp-border); position:sticky; top:0; z-index:100; }
.lp .nav-inner { display:flex; align-items:center; justify-content:space-between; padding-block:14px; }
.lp .logo { display:flex; align-items:center; gap:10px; text-decoration:none; color:var(--lp-text); }
.lp .logo-name { font-family:'Noto Serif JP',serif; font-weight:700; font-size:1.0625rem; letter-spacing:.04em; }
.lp .nav-right { display:flex; align-items:center; gap:28px; }
.lp .nav-link { text-decoration:none; color:var(--lp-text-2); font-size:.875rem; font-weight:500; transition:color .15s; }
.lp .nav-link:hover { color:var(--lp-accent); }

.lp .btn { display:inline-flex; align-items:center; gap:6px; padding:9px 20px; border-radius:6px; font-size:.875rem; font-weight:700; text-decoration:none; transition:all .15s; cursor:pointer; border:none; font-family:'Noto Sans JP',sans-serif; }
.lp .btn-primary { background:var(--lp-accent); color:#fff; }
.lp .btn-primary:hover { background:var(--lp-accent-h); }
.lp .btn-ghost { background:transparent; color:var(--lp-accent); border:1.5px solid var(--lp-border); }
.lp .btn-ghost:hover { border-color:var(--lp-accent); }
.lp .btn-lg { padding:13px 30px; font-size:.9375rem; }
.lp .btn-white { background:#fff; color:var(--lp-accent); }
.lp .btn-white:hover { background:rgba(255,255,255,.9); }

/* HERO */
.lp .hero { background:var(--lp-surface); border-bottom:1px solid var(--lp-border); padding-block:80px 72px; position:relative; overflow:hidden; }
.lp .hero::before { content:''; position:absolute; inset:0; background-image:linear-gradient(var(--lp-rule) 1px,transparent 1px),linear-gradient(90deg,var(--lp-rule) 1px,transparent 1px); background-size:48px 48px; pointer-events:none; }
.lp .hero-grid { display:grid; grid-template-columns:1fr 440px; gap:56px; align-items:center; position:relative; }
.lp .eyebrow { display:inline-block; font-size:.6875rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--lp-accent); background:var(--lp-accent-lt); border-radius:4px; padding:4px 10px; margin-bottom:22px; }
.lp .hero-title { margin-bottom:18px; }
.lp .hero-sub { color:var(--lp-text-2); font-size:.9375rem; margin-bottom:36px; line-height:1.85; }
.lp .hero-actions { display:flex; gap:12px; flex-wrap:wrap; }

/* DOC MOCKUP */
.lp .doc-wrap { display:flex; flex-direction:column; gap:12px; }
.lp .doc-card { background:var(--lp-surface); border:1px solid var(--lp-border); border-radius:var(--lp-r); box-shadow:var(--lp-sh-lg); overflow:hidden; font-size:.8125rem; }
.lp .doc-head { background:var(--lp-accent); color:#fff; padding:10px 16px; font-family:'Noto Serif JP',serif; font-size:.9375rem; font-weight:600; letter-spacing:.18em; text-align:center; }
.lp .doc-row { display:grid; grid-template-columns:110px 1fr; border-bottom:1px solid var(--lp-border); }
.lp .doc-row:last-child { border-bottom:none; }
.lp .doc-label { background:var(--lp-surface-2); border-right:1px solid var(--lp-border); padding:9px 12px; color:var(--lp-text-2); font-size:.75rem; display:flex; align-items:center; }
.lp .doc-val { padding:9px 12px; color:var(--lp-text); position:relative; display:flex; align-items:center; }
.lp .doc-val.hl-a { background:rgba(0,82,168,.09); }
.lp .doc-val.hl-b { background:rgba(0,122,87,.09); }
.lp .hl-chip { position:absolute; right:8px; top:50%; transform:translateY(-50%); font-size:.625rem; font-weight:700; padding:2px 7px; border-radius:3px; letter-spacing:.04em; }
.lp .hl-chip.a { background:var(--lp-accent); color:#fff; }
.lp .hl-chip.b { background:var(--lp-accent-2); color:#fff; }
.lp .extracted-card { background:var(--lp-surface); border:1px solid var(--lp-border); border-radius:var(--lp-r); box-shadow:var(--lp-sh); padding:14px 16px; }
.lp .ex-header { font-size:.6875rem; font-weight:700; letter-spacing:.09em; text-transform:uppercase; color:var(--lp-text-3); margin-bottom:10px; }
.lp .ex-row { display:flex; justify-content:space-between; gap:16px; padding-block:7px; border-bottom:1px solid var(--lp-border); font-size:.8125rem; }
.lp .ex-row:last-child { border-bottom:none; }
.lp .ex-key { color:var(--lp-text-2); }
.lp .ex-val { font-weight:500; color:var(--lp-text); }
.lp .ex-val.a { color:var(--lp-accent); }
.lp .ex-val.b { color:var(--lp-accent-2); }

@media (prefers-reduced-motion: no-preference) {
  .lp .hl-a { animation:lp-hl 3.6s ease-in-out infinite; }
  .lp .hl-b { animation:lp-hl 3.6s ease-in-out 1.8s infinite; }
  @keyframes lp-hl { 0%,100%{opacity:1}50%{opacity:.6} }
}

/* PROBLEM */
.lp .problem { padding-block:80px; }
.lp .sec-label { font-size:.6875rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--lp-text-3); margin-bottom:12px; }
.lp .sec-title { margin-bottom:48px; }
.lp .pain-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:20px; }
.lp .pain-card { background:var(--lp-surface); border:1px solid var(--lp-border); border-radius:var(--lp-r); padding:28px 22px; }
.lp .pain-icon { width:40px; height:40px; border-radius:8px; background:var(--lp-accent-lt); display:grid; place-items:center; color:var(--lp-accent); margin-bottom:16px; }
.lp .pain-title { font-family:'Noto Serif JP',serif; font-weight:600; font-size:.9375rem; margin-bottom:8px; }
.lp .pain-desc { color:var(--lp-text-2); font-size:.875rem; max-width:none; }

/* HOW IT WORKS */
.lp .how { padding-block:80px; background:var(--lp-surface); border-top:1px solid var(--lp-border); border-bottom:1px solid var(--lp-border); }
.lp .steps { display:grid; grid-template-columns:repeat(3,1fr); gap:0; position:relative; }
.lp .steps::before { content:''; position:absolute; top:27px; left:calc(100% / 6); right:calc(100% / 6); height:1px; background:var(--lp-border); }
.lp .step { padding-inline:28px; text-align:center; }
.lp .step-circle { width:54px; height:54px; border-radius:50%; background:var(--lp-surface); border:2px solid var(--lp-border); display:grid; place-items:center; margin:0 auto 22px; font-family:'Noto Serif JP',serif; font-weight:700; font-size:1.1875rem; color:var(--lp-accent); position:relative; z-index:1; }
.lp .step-title { font-family:'Noto Serif JP',serif; font-weight:600; font-size:.9375rem; margin-bottom:10px; }
.lp .step-desc { color:var(--lp-text-2); font-size:.875rem; line-height:1.75; max-width:220px; margin-inline:auto; }
.lp .step-tag { display:inline-block; margin-bottom:10px; font-size:.625rem; font-weight:700; letter-spacing:.06em; padding:3px 8px; border-radius:3px; }
.lp .step-tag.p1 { background:var(--lp-accent-lt); color:var(--lp-accent); }
.lp .step-tag.p2 { background:var(--lp-accent-2-lt); color:var(--lp-accent-2); }

/* FEATURES */
.lp .features { padding-block:80px; }
.lp .feature-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:20px; }
.lp .feature-card { background:var(--lp-surface); border:1px solid var(--lp-border); border-radius:var(--lp-r); padding:26px 22px; display:grid; grid-template-columns:44px 1fr; gap:18px; align-items:start; }
.lp .feature-icon { width:44px; height:44px; border-radius:8px; background:var(--lp-accent-lt); display:grid; place-items:center; color:var(--lp-accent); flex-shrink:0; }
.lp .feature-icon.g { background:var(--lp-accent-2-lt); color:var(--lp-accent-2); }
.lp .feature-title { font-weight:700; font-size:.9375rem; margin-bottom:6px; }
.lp .feature-desc { color:var(--lp-text-2); font-size:.875rem; max-width:none; }

/* CTA */
.lp .final-cta { padding-block:96px; background:var(--lp-accent); text-align:center; }
.lp .final-cta h2 { color:#fff; margin-bottom:14px; }
.lp .final-cta p { color:rgba(255,255,255,.78); margin-inline:auto; margin-bottom:36px; }

/* FOOTER */
.lp footer { background:var(--lp-surface); border-top:1px solid var(--lp-border); padding-block:36px; }
.lp .footer-inner { display:flex; align-items:center; justify-content:space-between; gap:20px; }
.lp .footer-copy { color:var(--lp-text-3); font-size:.8125rem; }

/* RESPONSIVE */
@media (max-width: 840px) {
  .lp .hero-grid { grid-template-columns:1fr; gap:44px; }
  .lp .pain-grid { grid-template-columns:1fr; }
  .lp .steps { grid-template-columns:1fr; gap:28px; }
  .lp .steps::before { display:none; }
  .lp .step { text-align:left; padding:0; display:grid; grid-template-columns:54px 1fr; gap:18px; align-items:start; }
  .lp .step-circle { margin:0; }
  .lp .step-desc { margin-inline:0; max-width:none; }
  .lp .feature-grid { grid-template-columns:1fr; }
  .lp .footer-inner { flex-direction:column; align-items:flex-start; }
}
@media (max-width: 560px) {
  .lp .nav-right .nav-link { display:none; }
}
`

export default function LandingPage() {
  return (
    <div className="lp">
      {/* eslint-disable-next-line react/no-danger */}
      <style dangerouslySetInnerHTML={{ __html: LP_CSS }} />

      {/* NAV */}
      <nav>
        <div className="lp-container">
          <div className="nav-inner">
            <a href="/" className="logo">
              <img src="/eq-ocr.png" alt="eq-OCR" style={{height:'34px', width:'auto'}} />
              <span className="logo-name">eq-OCR</span>
            </a>
            <div className="nav-right">
              <a href="#how" className="nav-link">仕組み</a>
              <a href="#features" className="nav-link">機能</a>
              <a href="/app" className="btn btn-primary">デモを試す</a>
            </div>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="lp-container">
          <div className="hero-grid">
            <div>
              <span className="eyebrow">AI書類読み取りサービス</span>
              <h1 className="hero-title">書類処理を、<br />AIに任せる。</h1>
              <p className="hero-sub">申請書・帳票・報告書など、あらゆる紙書類の情報をAIが自動で読み取ります。フォーマットを一度登録すれば、あとは書類を投げ込むだけ。</p>
              <div className="hero-actions">
                <a href="/app" className="btn btn-primary btn-lg">
                  デモを試す
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </a>
                <a href="#how" className="btn btn-ghost btn-lg">仕組みを見る</a>
              </div>
            </div>
            <div className="doc-wrap">
              <div className="doc-card">
                <div className="doc-head">申　請　書</div>
                <div className="doc-row">
                  <div className="doc-label">申請年月日</div>
                  <div className="doc-val hl-a">令和6年9月15日<span className="hl-chip a">抽出</span></div>
                </div>
                <div className="doc-row">
                  <div className="doc-label">申請者氏名</div>
                  <div className="doc-val hl-b">山田　太郎<span className="hl-chip b">抽出</span></div>
                </div>
                <div className="doc-row">
                  <div className="doc-label">申請者住所</div>
                  <div className="doc-val">東京都新宿区西新宿1丁目1番地</div>
                </div>
                <div className="doc-row">
                  <div className="doc-label">申請内容</div>
                  <div className="doc-val">住民票の写し（本人分）</div>
                </div>
              </div>
              <div className="extracted-card">
                <div className="ex-header">抽出された情報</div>
                <div className="ex-row">
                  <span className="ex-key">申請年月日</span>
                  <span className="ex-val a">令和6年9月15日</span>
                </div>
                <div className="ex-row">
                  <span className="ex-key">申請者氏名</span>
                  <span className="ex-val b">山田　太郎</span>
                </div>
                <div className="ex-row">
                  <span className="ex-key">申請者住所</span>
                  <span className="ex-val">東京都新宿区西新宿1丁目1番地</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PROBLEM */}
      <section className="problem">
        <div className="lp-container">
          <p className="sec-label">課題</p>
          <h2 className="sec-title">書類処理に費やす時間を削減する</h2>
          <div className="pain-grid">
            <div className="pain-card">
              <div className="pain-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <div className="pain-title">転記作業に時間がかかる</div>
              <p className="pain-desc">書類から情報を手で入力する作業は時間がかかるだけでなく、ミスの温床になります。</p>
            </div>
            <div className="pain-card">
              <div className="pain-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </div>
              <div className="pain-title">書類ごとにレイアウトが違う</div>
              <p className="pain-desc">申請書の種類や取引先によってフォーマットが異なり、汎用OCRでは対応しきれません。</p>
            </div>
            <div className="pain-card">
              <div className="pain-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
                </svg>
              </div>
              <div className="pain-title">処理量に比例してコストが増える</div>
              <p className="pain-desc">書類が増えるほど人員も増やす必要があり、品質のばらつきも大きくなります。</p>
            </div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="how" id="how">
        <div className="lp-container">
          <p className="sec-label">仕組み</p>
          <h2 className="sec-title" style={{ marginBottom: '56px' }}>2つのフェーズで完全自動化</h2>
          <div className="steps">
            <div className="step">
              <div className="step-circle">1</div>
              <div>
                <span className="step-tag p1">Phase 1</span>
                <div className="step-title">フォーマット登録</div>
                <p className="step-desc">書類の種別名と抽出したい項目（氏名・日付・金額など）を指定し、サンプル書類をアップロードします。</p>
              </div>
            </div>
            <div className="step">
              <div className="step-circle">2</div>
              <div>
                <span className="step-tag p1">Phase 1</span>
                <div className="step-title">AI学習</div>
                <p className="step-desc">Google Cloud Vision と GPT-4o が書類の構造を解析し、各項目の位置をテンプレートとして自動保存します。</p>
              </div>
            </div>
            <div className="step">
              <div className="step-circle">3</div>
              <div>
                <span className="step-tag p2">Phase 2</span>
                <div className="step-title">自動抽出</div>
                <p className="step-desc">以後は同種の書類をアップロードするだけ。テンプレートを使い、指定項目を即座に抽出します。</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="features" id="features">
        <div className="lp-container">
          <p className="sec-label">機能</p>
          <h2 className="sec-title" style={{ marginBottom: '48px' }}>高精度な抽出を支える技術</h2>
          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                </svg>
              </div>
              <div>
                <div className="feature-title">高精度OCR</div>
                <p className="feature-desc">Google Cloud Vision APIによる文字認識。日本語の印刷・手書き文字を問わず、複雑なレイアウトでも高い精度で読み取ります。</p>
              </div>
            </div>
            <div className="feature-card">
              <div className="feature-icon g">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
                </svg>
              </div>
              <div>
                <div className="feature-title">LLMによる文脈理解</div>
                <p className="feature-desc">GPT-4oが書類の文脈を読み取り、単純な座標マッチングでは困難な曖昧な項目も正確に特定・抽出します。</p>
              </div>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div>
                <div className="feature-title">PDF・画像対応</div>
                <p className="feature-desc">PDF、PNG、JPEGなど主要フォーマットに対応。スキャン書類もスマートフォン撮影画像も処理できます。</p>
              </div>
            </div>
            <div className="feature-card">
              <div className="feature-icon g">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
                </svg>
              </div>
              <div>
                <div className="feature-title">組織アカウント管理</div>
                <p className="feature-desc">組織単位でテンプレートを管理。メンバー全員が同じテンプレートを共有でき、情報の分散を防ぎます。</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="final-cta">
        <div className="lp-container">
          <h2>まずはデモで試してみる</h2>
          <p>登録不要。書類をアップロードするだけで、AIの抽出精度をご確認いただけます。</p>
          <a href="/app" className="btn btn-white btn-lg">
            デモを試す
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
        </div>
      </section>

      {/* FOOTER */}
      <footer>
        <div className="lp-container">
          <div className="footer-inner">
            <a href="/" className="logo">
              <img src="/eq-ocr.png" alt="eq-OCR" style={{height:'34px', width:'auto'}} />
              <span className="logo-name">eq-OCR</span>
            </a>
            <p className="footer-copy">© 2026 eq-OCR. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
