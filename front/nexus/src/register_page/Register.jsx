import { useState } from "react";
import { Link } from "react-router-dom";
import "./Register.css";

export default function Register() {
    const [name, setName] = useState("");
    const [login, setLogin] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);


    async function handleSubmit(event) {
        event.preventDefault();
        if (isSubmitting) return;

        setError("");
        setMessage("");

        if (!name.trim()) {
            setError("Digite seu nome.");
            return;
        }

        if (password !== confirmPassword) {
            setError("As senhas não coincidem.");
            return;
        }
        setIsSubmitting(true);

        try {
            const response = await fetch("http://localhost:8000/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    login: login.trim(),
                    password,
                    name: name.trim()
                }),
            });

            if (response.status === 409) throw new Error("Esse login já está em uso. Escolha outro.");
            if (!response.ok) {
                throw new Error(`Não foi possível criar a conta (${response.status}).`);
            }

            setMessage("Conta criada! Você já pode entrar.");
            setPassword("");
            setConfirmPassword("");
        } catch (error) {
            setError(error instanceof TypeError ? "Não foi possível conectar à API." : error.message);
        } finally {
            setIsSubmitting(false);
        }

    }

    return (
        <main className="register-page">
            <section
                className="register-card"
                aria-labelledby="register-title"
            >
                <div className="register-brand">NEXUS</div>

                <header className="register-heading">
          <span className="register-icon" aria-hidden="true">
            ✨
          </span>

                    <h1 id="register-title">Comece sua próxima história.</h1>
                    <p>Crie sua conta e organize seus filmes, jogos e livros.</p>
                </header>

                <form className="register-form" onSubmit={handleSubmit}>
                    <div className="register-field">
                        <label htmlFor="register-name">Nome</label>

                        <input
                            id="register-name"
                            name="name"
                            type="text"
                            placeholder="Seu nome"
                            autoComplete="name"
                            maxLength={100}
                            value={name}
                            onChange={(event) => setName(event.target.value)}
                            required
                        />
                    </div>

                    <div className="register-field">
                        <label htmlFor="register-login">Login</label>

                        <input
                            id="register-login"
                            name="login"
                            type="text"
                            placeholder="seu_login"
                            autoComplete="username"
                            minLength={3}
                            maxLength={50}
                            pattern="[a-zA-Z0-9_.-]+"
                            title="Use de 3 a 50 letras, números, pontos, hífens ou sublinhados, sem espaços."
                            value={login}
                            onChange={(event) => setLogin(event.target.value)}
                            required
                        />
                    </div>

                    <div className="register-field">
                        <label htmlFor="register-password">Senha</label>

                        <input
                            id="register-password"
                            name="password"
                            type="password"
                            placeholder="Crie uma senha"
                            minLength={8}
                            maxLength={64}
                            autoComplete="new-password"
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            required
                        />
                    </div>

                    <div className="register-field">
                        <label htmlFor="register-confirm-password">
                            Confirmar senha
                        </label>

                        <input
                            id="register-confirm-password"
                            name="confirmPassword"
                            type="password"
                            placeholder="Digite a senha novamente"
                            autoComplete="new-password"
                            value={confirmPassword}
                            onChange={(event) => {
                                setConfirmPassword(event.target.value);
                                setError("");
                            }}
                            aria-invalid={error ? true : undefined}
                            aria-describedby={error ? "register-error" : undefined}
                            required
                        />
                    </div>

                    {error && (
                        <p id="register-error" className="register-error" role="alert">
                            {error}
                        </p>
                    )}

                    <button className="register-submit" type="submit" disabled={isSubmitting}>
                        {isSubmitting ? "Criando conta…" : "Criar conta"}
                    </button>

                    <p className="register-message" role="status">
                        {message}
                    </p>
                </form>

                <p className="register-login">
                    Já tem uma conta? <Link to="/login">Entrar</Link>
                </p>

                <footer className="register-footer">
                    Filmes, jogos e livros. Tudo no seu ritmo.
                </footer>
            </section>
        </main>
    );
}