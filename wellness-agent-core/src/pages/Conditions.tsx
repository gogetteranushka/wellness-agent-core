import React, { useEffect, useState } from "react";
import { supabase } from "../../supabaseClient";

function Conditions() {
  const [conditions, setConditions] = useState([]);
  const [form, setForm] = useState({ condition_name: "", diagnosed_date: "", notes: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    async function fetchConditions() {
      setLoading(true);
      setError(null);
      try {
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;
        const res = await fetch("http://localhost:5000/api/condition", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Failed to fetch conditions");
        const data = await res.json();
        setConditions(data);
      } catch(err) {
        setError(err.message);
      }
      setLoading(false);
    }
    fetchConditions();
  }, []);

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      const res = await fetch("http://localhost:5000/api/condition", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error("Failed to add condition");
      setSuccess("Condition added!");
      // Optionally refresh list here
    } catch(err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>Condition Name: <input name="condition_name" value={form.condition_name} onChange={handleChange} /></label>
        <label>Diagnosed Date: <input name="diagnosed_date" type="date" value={form.diagnosed_date} onChange={handleChange} /></label>
        <label>Notes: <input name="notes" value={form.notes} onChange={handleChange} /></label>
        <button type="submit">Add Condition</button>
      </form>
      {loading && <p>Loading conditions...</p>}
      {error && <p style={{color:"red"}}>{error}</p>}
      <h3>Your Health Conditions</h3>
      <ul>
        {conditions.map((c, i) => (
          <li key={i}>{c.condition_name} - {c.diagnosed_date}</li>
        ))}
      </ul>
      {success && <p style={{color:"green"}}>{success}</p>}
    </div>
  );
}

export default Conditions;
