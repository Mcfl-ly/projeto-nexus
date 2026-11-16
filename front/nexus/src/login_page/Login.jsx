import { apiUrl } from "../api.js";
import { useState } from "react";
import "./Login.css";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
    const navigate = useNavigate();
    const [login, setLogin] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    async function handleSubmit(event) {
        event.preventDefault();

        if (isSubmitting) return;
        setMessage("");
        setIsSubmitting(true);
        try {
            const response = await fetch(apiUrl("/login"), {
                method: "POST", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ login: login.trim(), password }),
            });
            const data = await response.json().catch(() => null);
            if (!response.ok) throw new Error(typeof data?.detail === "string" ? data.detail : "Não foi possível entrar. Confira seu login e senha.");
            navigate("/", { replace: true });
        } catch (error) {
            setMessage(error instanceof TypeError ? "Não foi possível conectar à API." : error.message);
        } finally { setIsSubmitting(false); }

    }

    return (
        <main className="login-page">
            <section className="login-card" aria-labelledby="login-title">
                <div className="login-brand">NEXUS</div>

                <header className="login-heading">
          <span className="login-icon" aria-hidden="true">
            ✨
          </span>

                    <h1 id="login-title">Sua próxima história começa aqui.</h1>
                    <p>Entre para acompanhar seus filmes, jogos e livros.</p>
                </header>

                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="login-field">
                        <label htmlFor="login">Login</label>

                        <input
                            id="login"
                            name="login"
                            type="text"
                            placeholder="seu_login"
                            autoComplete="username"
                            minLength={3}
                            maxLength={50}
                            value={login}
                            onChange={(event) => setLogin(event.target.value)}
                            required
                        />
                    </div>

                    <div className="login-field">
                        <label htmlFor="password">Senha</label>

                        <input
                            id="password"
                            name="password"
                            type="password"
                            placeholder="Digite sua senha"
                            autoComplete="current-password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            required
                        />
                    </div>

                    <button className="login-submit" type="submit" disabled={isSubmitting}>
                        {isSubmitting ? "Entrando…" : "Entrar"}
                    </button>

                    <p className="login-message" role="status">
                        {message}
                    </p>
                </form>
                <p className="login-register">
                    Ainda não tem uma conta?{" "}
                    <Link to="/cadastro">Cadastre-se</Link>
                </p>
                <footer className="login-footer">
                    Filmes, jogos e livros. Tudo no seu ritmo.
                </footer>
            </section>
        </main>
    );
}