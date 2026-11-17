import useLibrary from "../hooks/useLibrary.js";
import { apiUrl } from "../api.js";
import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import Header from "../Components/Header.jsx";
import "./Profile.css";

async function updateProfile(path, body) {
    const response = await fetch(apiUrl("") + path, {
        method: "PATCH", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
        throw new Error(response.status === 401 ? "Sua sessão expirou. Entre novamente para continuar." : typeof data?.detail === "string" ? data.detail : "Não foi possível salvar. Confira os dados e tente novamente.");
    }
    return data;
}

export default function Profile() {
    const { user, setUser } = useOutletContext();
    const [name, setName] = useState(user.username ?? "");
    const [savedName, setSavedName] = useState(user.username ?? "");
    const [password, setPassword] = useState("");
    const [confirmation, setConfirmation] = useState("");
    const [savingName, setSavingName] = useState(false);
    const [savingPassword, setSavingPassword] = useState(false);
    const [nameError, setNameError] = useState("");
    const [nameMessage, setNameMessage] = useState("");
    const [passwordError, setPasswordError] = useState("");
    const [passwordMessage, setPasswordMessage] = useState("");
    const { library, libraryError: totalError, loadingLibrary, reloadLibrary } = useLibrary();
    const total = loadingLibrary ? null : library.length;

    async function saveName(event) {
        event.preventDefault();
        if (savingName) return;
        setNameError(""); setNameMessage("");
        const trimmed = name.trim();
        if (!trimmed) { setNameError("Digite seu nome."); return; }
        setSavingName(true);
        try {
            const data = await updateProfile("/users/me", { username: trimmed });
            setName(data.name); setSavedName(data.name);
            setUser((current) => ({ ...current, username: data.name }));
            setNameMessage("Nome atualizado com sucesso.");
        } catch (error) {
            setNameError(error instanceof TypeError ? "Não foi possível conectar à API." : error.message);
        } finally { setSavingName(false); }
    }

    async function savePassword(event) {
        event.preventDefault();
        if (savingPassword) return;
        setPasswordError(""); setPasswordMessage("");
        if (password !== confirmation) { setPasswordError("As senhas não coincidem."); return; }
        if (password.length < 8 || password.length > 64) { setPasswordError("Use uma senha com 8 a 64 caracteres."); return; }
        setSavingPassword(true);
        try {
            await updateProfile("/users/me/password", { password });
            setPassword(""); setConfirmation("");
            setPasswordMessage("Senha alterada com sucesso.");
        } catch (error) {
            setPasswordError(error instanceof TypeError ? "Não foi possível conectar à API." : error.message);
        } finally { setSavingPassword(false); }
    }

    return <>
        <Header username={savedName} />
        <main className="profile-page">
            <header className="profile-heading"><h1>Meu perfil</h1><p>Cuide dos seus dados e acompanhe sua biblioteca.</p></header>
            <section className="profile-summary" aria-labelledby="profile-library-title">
                <div className="profile-avatar" aria-hidden="true">{savedName.trim().charAt(0).toLocaleUpperCase() || "👤"}</div>
                <div className="profile-welcome"><h2>{savedName}</h2><p>Sua biblioteca, do seu jeito.</p></div>
                <div className="profile-total"><h3 id="profile-library-title">Conteúdos adicionados</h3>
                    {totalError ? <><p role="alert">{totalError}</p><button type="button" onClick={reloadLibrary}>Tentar novamente</button></> : <><strong>{total === null ? "…" : total}</strong><p>Filmes, jogos e livros no total</p></>}
                </div>
            </section>
            <div className="profile-forms">
                <section className="profile-panel" aria-labelledby="profile-name-title">
                    <h2 id="profile-name-title">Alterar nome</h2><p>Como você quer aparecer no Nexus?</p>
                    <form onSubmit={saveName} aria-busy={savingName}>
                        <label htmlFor="profile-name">Nome</label>
                        <input id="profile-name" autoComplete="name" value={name} onChange={(event) => { setName(event.target.value); setNameMessage(""); setNameError(""); }} required maxLength={100} disabled={savingName} aria-invalid={Boolean(nameError)} aria-describedby={nameError ? "profile-name-error" : undefined} />
                        {nameError && <p id="profile-name-error" className="profile-error" role="alert">{nameError}</p>}
                        {nameMessage && <p className="profile-success" role="status">{nameMessage}</p>}
                        <button type="submit" disabled={savingName || name.trim() === savedName}>{savingName ? "Salvando…" : "Salvar nome"}</button>
                    </form>
                </section>
                <section className="profile-panel" aria-labelledby="profile-password-title">
                    <h2 id="profile-password-title">Alterar senha</h2><p>Escolha uma senha com 8 a 64 caracteres.</p>
                    <form onSubmit={savePassword} aria-busy={savingPassword}>
                        <label htmlFor="profile-password">Nova senha</label>
                        <input id="profile-password" type="password" autoComplete="new-password" value={password} onChange={(event) => { setPassword(event.target.value); setPasswordMessage(""); setPasswordError(""); }} required minLength={8} maxLength={64} disabled={savingPassword} />
                        <label htmlFor="profile-password-confirm">Confirmar nova senha</label>
                        <input id="profile-password-confirm" type="password" autoComplete="new-password" value={confirmation} onChange={(event) => { setConfirmation(event.target.value); setPasswordError(""); setPasswordMessage(""); }} required minLength={8} maxLength={64} disabled={savingPassword} aria-invalid={Boolean(passwordError)} aria-describedby={passwordError ? "profile-password-error" : undefined} />
                        {passwordError && <p id="profile-password-error" className="profile-error" role="alert">{passwordError}</p>}
                        {passwordMessage && <p className="profile-success" role="status">{passwordMessage}</p>}
                        <button type="submit" disabled={savingPassword}>{savingPassword ? "Salvando…" : "Salvar nova senha"}</button>
                    </form>
                </section>
            </div>
        </main>
    </>;
}
