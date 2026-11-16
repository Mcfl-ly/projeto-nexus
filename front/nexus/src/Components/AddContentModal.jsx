import { useEffect, useRef, useState } from "react";
import "./AddContentModal.css";

const TYPES = {
    movie: { label: "filme", icon: "🎬", provider: "TMDB", author: "Direção", status: "Quero Assistir" },
    game: { label: "jogo", icon: "🎮", provider: "IGDB", status: "Quero Jogar" },
    book: { label: "livro", icon: "📖", provider: "Open Library", author: "Autores", status: "Quero Ler" },
};

export default function AddContentModal({ type, onClose, onAdded }) {
    const config = TYPES[type];
    const dialogRef = useRef(null);
    const [mode, setMode] = useState("search");
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");

    useEffect(() => {
        const dialog = dialogRef.current;
        const trigger = document.activeElement;
        const overflow = document.body.style.overflow;
        dialog.showModal();
        document.body.style.overflow = "hidden";
        return () => {
            dialog.close();
            document.body.style.overflow = overflow;
            trigger?.focus();
        };
    }, []);

    async function submit(event) {
        event.preventDefault();
        if (saving) return;
        const form = new FormData(event.currentTarget);
        const title = String(form.get("title") || "").trim();
        setError("");
        setNotice("");
        if (!title) {
            setError("Digite o título do conteúdo.");
            return;
        }
        const payload = { title, type };
        if (mode === "manual") {
            const split = (name) => String(form.get(name) || "").split(",").map((value) => value.trim()).filter(Boolean);
            const image = String(form.get("img_url") || "").trim();
            if (image && !/^https?:\/\//i.test(image)) {
                setError("Use um endereço de capa começando com http:// ou https://.");
                return;
            }
            Object.assign(payload, {
                release_date: form.get("release_date") || null,
                genres: split("genres"),
                img_url: image || null,
            });
            if (config.author) payload.author = split("author");
        }
        setSaving(true);
        try {
            const response = await fetch(mode === "manual" ? "http://localhost:8000/library/manual" : "http://localhost:8000/library", {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await response.json().catch(() => null);
            if (!response.ok) {
                throw new Error(typeof data?.detail === "string" ? data.detail : response.status === 401 ? "Sua sessão expirou. Entre novamente para adicionar conteúdo." : "Não foi possível adicionar. Confira os dados e tente novamente.");
            }
            if (typeof data === "string" && data.includes("já existe")) {
                setNotice(data);
                return;
            }
            onAdded();
        } catch (failure) {
            setError(failure instanceof TypeError ? "Não foi possível conectar à API. Tente novamente." : failure.message);
        } finally {
            setSaving(false);
        }
    }

    return (
        <dialog ref={dialogRef} className={"add-content-modal add-content-" + type} aria-labelledby="add-content-title"
            onCancel={(event) => { event.preventDefault(); if (!saving) onClose(); }}
            onClick={(event) => {
                if (event.target !== event.currentTarget || saving) return;
                const bounds = event.currentTarget.getBoundingClientRect();
                if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) onClose();
            }}>
            <header className="add-content-heading">
                <div><span className="add-content-icon" aria-hidden="true">{config.icon}</span>
                    <h2 id="add-content-title">Adicionar {config.label}</h2>
                    <p>Mais uma história para sua biblioteca.</p>
                </div>
                <button className="add-content-close" type="button" onClick={onClose} disabled={saving} aria-label="Fechar janela">×</button>
            </header>
            <div className="add-content-modes" role="group" aria-label="Forma de adicionar">
                <button type="button" aria-pressed={mode === "search"} disabled={saving} onClick={() => { setMode("search"); setError(""); setNotice(""); }}>Buscar pelo título</button>
                <button type="button" aria-pressed={mode === "manual"} disabled={saving} onClick={() => { setMode("manual"); setError(""); setNotice(""); }}>Cadastro manual</button>
            </div>
            <form onSubmit={submit} className="add-content-form" aria-busy={saving}>
                <p className="add-content-hint">{mode === "search" ? "Buscaremos na " + config.provider + " e adicionaremos o primeiro resultado com os dados disponíveis." : "Preencha os detalhes. Apenas o título é obrigatório."}</p>
                <fieldset disabled={saving}>
                    <label htmlFor="add-title">Título *</label>
                    <input id="add-title" name="title" type="text" maxLength={500} required autoFocus placeholder={type === "movie" ? "Ex.: Interestelar" : type === "game" ? "Ex.: Stardew Valley" : "Ex.: Dom Casmurro"} />
                    {mode === "manual" && <>
                        {config.author && <><label htmlFor="add-author">{config.author}</label><input id="add-author" name="author" placeholder="Separe os nomes por vírgulas" /></>}
                        <label htmlFor="add-release">{type === "book" ? "Data de publicação" : "Data de lançamento"}</label>
                        <input id="add-release" name="release_date" type="date" />
                        <label htmlFor="add-genres">Gêneros</label>
                        <input id="add-genres" name="genres" placeholder="Ex.: Aventura, Fantasia" />
                        <label htmlFor="add-image">Endereço da capa</label>
                        <input id="add-image" name="img_url" type="url" placeholder="https://exemplo.com/capa.jpg" />
                    </>}
                </fieldset>
                <p className="add-content-hint">Lista inicial: <strong>{config.status}</strong>. Você pode alterar o status depois.</p>
                {error && <p className="add-content-error" role="alert">{error}</p>}
                {notice && <p className="add-content-notice" role="status">{notice}</p>}
                <footer className="add-content-footer">
                    <button type="button" onClick={onClose} disabled={saving}>Cancelar</button>
                    <button className="add-content-submit" type="submit" disabled={saving}>{saving ? "Adicionando…" : mode === "search" ? "Buscar e adicionar" : "Adicionar " + config.label}</button>
                </footer>
            </form>
        </dialog>
    );
}
