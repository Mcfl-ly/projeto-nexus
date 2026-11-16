import { apiUrl } from "../api.js";
import { useState } from "react";
import "./FavoriteButton.css";

export default function FavoriteButton({ id, title, favorite, onChanged }) {
    const [saved, setSaved] = useState(null);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const active = saved ?? Boolean(favorite);

    async function toggle() {
        if (saving) return;
        setSaving(true);
        setError("");
        try {
            const response = await fetch(apiUrl("/library/") + id + "/favorite", {
                method: "PATCH", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ favorite: !active }),
            });
            const data = await response.json().catch(() => null);
            if (!response.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Não foi possível salvar o favorito.");
            setSaved(data.favorite);
            onChanged?.();
        } catch (failure) {
            setError(failure instanceof TypeError ? "Não foi possível conectar à API." : failure.message);
        } finally {
            setSaving(false);
        }
    }

    return <div className="favorite-control">
        <button className="favorite-button" type="button" aria-pressed={active} disabled={saving}
            aria-busy={saving} aria-label={(active ? "Remover dos favoritos: " : "Favoritar: ") + title}
            title={active ? "Remover dos favoritos" : "Adicionar aos favoritos"} onClick={toggle}>
            <span aria-hidden="true">{saving ? "…" : active ? "♥" : "♡"}</span>
        </button>
        {error && <span className="favorite-error" role="alert">{error}</span>}
    </div>;
}
