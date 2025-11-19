import React, { useEffect, useState } from "react";
import { supabase } from "../../supabaseClient";

function NutritionLog() {
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState({ meal_type: "", food_name: "", calories: "", protein: "", carbohydrates: "", fat: "", fiber: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    async function fetchLogs() {
      setLoading(true);
      setError(null);
      try {
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;
        const res = await fetch("http://localhost:5000/api/nutrition-log", {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Failed to fetch nutrition logs");
        const data = await res.json();
        setLogs(data);
      } catch (err) {
        setError(err.message);
      }
      setLoading(false);
    }
    fetchLogs();
  }, []);

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async e => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;
      const body = {
        meal_type: form.meal_type,
        food_name: form.food_name,
        calories: parseInt(form.calories),
        protein: parseInt(form.protein),
        carbohydrates: parseInt(form.carbohydrates),
        fat: parseInt(form.fat),
        fiber: parseInt(form.fiber),
      };
      const res = await fetch("http://localhost:5000/api/nutrition-log", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error("Failed to log meal");
      setSuccess("Meal logged!");
      // Optionally refresh logs here
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>Meal Type: <input name="meal_type" value={form.meal_type} onChange={handleChange} /></label>
        <label>Food Name: <input name="food_name" value={form.food_name} onChange={handleChange} /></label>
        <label>Calories: <input name="calories" value={form.calories} onChange={handleChange} /></label>
        <label>Protein: <input name="protein" value={form.protein} onChange={handleChange} /></label>
        <label>Carbohydrates: <input name="carbohydrates" value={form.carbohydrates} onChange={handleChange} /></label>
        <label>Fat: <input name="fat" value={form.fat} onChange={handleChange} /></label>
        <label>Fiber: <input name="fiber" value={form.fiber} onChange={handleChange} /></label>
        <button type="submit">Log Meal</button>
      </form>
      {loading && <p>Loading meals...</p>}
      {error && <p style={{color:"red"}}>{error}</p>}
      <h3>Meals</h3>
      <ul>
        {logs.map(log => (
          <li key={log.id}>{log.meal_type} - {log.food_name} ({log.calories} kcal)</li>
        ))}
      </ul>
      {success && <p style={{color:"green"}}>{success}</p>}
    </div>
  );
}

export default NutritionLog;
