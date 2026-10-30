import { useState } from "react";
import "./Login.css";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");

    async function handleSubmit(event) {
        event.preventDefault();

        setMessage(
            "Formulário pronto. Falta conectar à sua rota de login."
        );

        const response = await fetch("http://localhost:8000/login", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: email,
                password,
            }),
        });
        if (response.ok) {
            setMessage("Login efetuado.");
            navigate("/", { replace: true });

        }
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
                        <label htmlFor="email">E-mail</label>

                        <input
                            id="email"
                            name="email"
                            type="email"
                            placeholder="voce@exemplo.com"
                            autoComplete="username"
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
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

                    <button className="login-submit" type="submit">
                        Entrar
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