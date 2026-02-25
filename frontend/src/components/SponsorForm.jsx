export default function SponsorForm({ sponsorInfo, onChange }) {
  return (
    <div className="sponsor-form">
      <div className="form-group">
        <label className="form-label">
          Sponsor / Company Name
          <span className="required">*</span>
        </label>
        <input
          type="text"
          className="form-input"
          placeholder="e.g., Acme Corp"
          value={sponsorInfo.sponsor_name}
          onChange={(e) => onChange('sponsor_name', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Sales Rep Name</label>
        <input
          type="text"
          className="form-input"
          placeholder="Your name"
          value={sponsorInfo.rep_name}
          onChange={(e) => onChange('rep_name', e.target.value)}
        />
      </div>

      <div className="form-group">
        <label className="form-label">Email</label>
        <input
          type="email"
          className="form-input"
          placeholder="name@example.com"
          value={sponsorInfo.sponsor_email}
          onChange={(e) => onChange('sponsor_email', e.target.value)}
        />
      </div>
    </div>
  )
}
