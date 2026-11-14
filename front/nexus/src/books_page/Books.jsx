import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import Header from "../components/Header.jsx";
import useLibrary from "../hooks/useLibrary";
import "./Books.css";

const COLUNAS = [
    {
        id: "to-read-title",
        titulo: "Quero ler",
        status: "Quero Ler",
        proximoStatus: "Lendo",
        acao: "Começar leitura",
        classeStatus: "book-status-pending",
    },
    {
        id: "reading-title",
        titulo: "Lendo",
        status: "Lendo",
        proximoStatus: "Lido",
        acao: "Marcar como lido",
        classeStatus: "book-status-reading",
    },
    {
        id: "read-title",
        titulo: "Lidos",
        status: "Lido",
        proximoStatus: "Quero Ler",
        acao: "Mover para quero ler",
        classeStatus: "book-status-read",
    },
];

export default function Books() {


    const [excluindo, setExcluindo] = useState({});
    const [idsExcluidos, setIdsExcluidos] = useState([]);
    const [erroExclusao, setErroExclusao] = useState("");


    const context = useOutletContext();
    const user = context?.user;

    const {
        fullContent,
        libraryError,
        loadingLibrary,
    } = useLibrary(user?.id);

    const [statusAtualizados, setStatusAtualizados] = useState({});
    const [atualizando, setAtualizando] = useState({});
    const [erroStatus, setErroStatus] = useState("");

    useEffect(() => {
        setStatusAtualizados({});
        setAtualizando({});
        setErroStatus("");
    }, [user?.id]);

    async function alterarStatus(livro, novoStatus) {
        const id = livro.registroId;

        if (atualizando[id]) return;

        setErroStatus("");
        setAtualizando((anterior) => ({
            ...anterior,
            [id]: true,
        }));

        try {
            const response = await fetch(
                `http://localhost:8000/library/${id}`,
                {
                    method: "PATCH",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        status: novoStatus,
                    }),
                }
            );

            if (!response.ok) {
                const erro = await response.json().catch(() => null);

                throw new Error(
                    typeof erro?.detail === "string"
                        ? erro.detail
                        : `Não foi possível alterar o status (${response.status}).`
                );
            }

            const dados = await response.json();

            setStatusAtualizados((anterior) => ({
                ...anterior,
                [id]: dados.status,
            }));
        } catch (error) {
            setErroStatus(error.message);
        } finally {
            setAtualizando((anterior) => ({
                ...anterior,
                [id]: false,
            }));
        }
    }

    async function excluirConteudo(registroId) {
        if (excluindo[registroId]) return;

        setErroExclusao("");
        setExcluindo((anterior) => ({
            ...anterior,
            [registroId]: true,
        }));

        try {
            const response = await fetch(
                `http://localhost:8000/library/${registroId}`,
                {
                    method: "DELETE",
                    credentials: "include",
                }
            );

            if (!response.ok) {
                const erro = await response.json().catch(() => null);

                throw new Error(
                    typeof erro?.detail === "string"
                        ? erro.detail
                        : `Não foi possível excluir o conteúdo (${response.status}).`
                );
            }

            // Sua rota não retorna dados; não é necessário chamar response.json().
            setIdsExcluidos((anterior) => [
                ...anterior,
                registroId,
            ]);
        } catch (error) {
            setErroExclusao(error.message);
        } finally {
            setExcluindo((anterior) => ({
                ...anterior,
                [registroId]: false,
            }));
        }
    }


    if (!user || user.id == null) {
        return <p>Usuário não identificado.</p>;
    }

    if (loadingLibrary) {
        return <p>Carregando livros...</p>;
    }

    if (libraryError) {
        return <p role="alert">{libraryError}</p>;
    }

    const conteudosPorId = new Map(
        fullContent.map((conteudo) => [
            String(conteudo._id),
            conteudo,
        ])
    );

    const livros = (user.content ?? [])
        .filter((registro) => !idsExcluidos.includes(registro.id))
        .flatMap((registro) => {
            const conteudo = conteudosPorId.get(
                String(registro.mongo_id)
            );

            if (!conteudo || conteudo.type !== "book") {
                return [];
            }

            return [{
                ...conteudo,
                registroId: registro.id,
                statusUsuario:
                    statusAtualizados[registro.id] ?? registro.status,
                notaUsuario: registro.rating,
            }];
        });

    return (
        <>
            <Header />

            <div className="books-page">
                <main className="books-content">
                    <section
                        className="books-heading"
                        aria-labelledby="books-title"
                    >
                        <div>
                            <h1 id="books-title">📖 Meus livros</h1>
                            <p>
                                Descubra novas leituras e acompanhe seu progresso.
                            </p>
                        </div>

                        <button className="add-book-button" type="button">
                            + Adicionar livro
                        </button>
                    </section>

                    {erroStatus && (
                        <p role="alert">{erroStatus}</p>
                    )}

                    <div className="books-columns">
                        {COLUNAS.map((coluna) => {
                            const livrosDaColuna = livros.filter(
                                (livro) => livro.statusUsuario === coluna.status
                            );

                            return (
                                <section
                                    key={coluna.id}
                                    className="book-column"
                                    aria-labelledby={coluna.id}
                                >
                                    <header className="book-column-header">
                                        <h2 id={coluna.id}>
                      <span
                          className={`book-status-dot ${coluna.classeStatus}`}
                          aria-hidden="true"
                      />
                                            {coluna.titulo}
                                        </h2>

                                        <span className="book-count">
                      {livrosDaColuna.length}
                    </span>
                                    </header>

                                    {livrosDaColuna.length === 0 ? (
                                        <p>Nenhum livro nesta lista.</p>
                                    ) : (
                                        <ul className="book-list">
                                            {livrosDaColuna.map((livro) => {
                                                const salvando = Boolean(
                                                    atualizando[livro.registroId]
                                                );

                                                return (
                                                    <li key={livro.registroId}>
                                                        <article className="book-card">
                                                            <div className="book-cover">
                                                                {livro.poster ? (
                                                                    <img
                                                                        src={livro.poster}
                                                                        alt={`Capa de ${livro.title}`}
                                                                    />
                                                                ) : (
                                                                    <span>Sem capa</span>
                                                                )}
                                                            </div>

                                                            <div className="book-info">
                                                                <h3>{livro.title}</h3>

                                                                <p className="book-author">
                                                                    {livro.author ??
                                                                        livro.authors?.join(", ")}
                                                                </p>

                                                                <ul
                                                                    className="book-genres"
                                                                    aria-label="Gêneros"
                                                                >
                                                                    {(livro.genres ?? []).map(
                                                                        (genero, index) => (
                                                                            <li key={`${genero}-${index}`}>
                                                                                {genero}
                                                                            </li>
                                                                        )
                                                                    )}
                                                                </ul>

                                                                {livro.notaUsuario != null && (
                                                                    <p className="book-rating">
                                                                        Nota: {livro.notaUsuario}
                                                                    </p>
                                                                )}
                                                            </div>

                                                            <div className="book-actions">
                                                                <button
                                                                    type="button"
                                                                    onClick={() => excluirConteudo(livro.registroId)}
                                                                    disabled={
                                                                        excluindo[livro.registroId] ||
                                                                        atualizando[livro.registroId]
                                                                    }
                                                                    aria-label={`Excluir ${livro.title} da biblioteca`}
                                                                >
                                                                    x
                                                                </button>

                                                                <button
                                                                    type="button"
                                                                    onClick={() =>
                                                                        alterarStatus(
                                                                            livro,
                                                                            coluna.proximoStatus
                                                                        )
                                                                    }
                                                                    disabled={salvando}
                                                                    aria-label={`${coluna.acao}: ${livro.title}`}
                                                                    title={coluna.acao}
                                                                    aria-busy={salvando}
                                                                >
                                                                    {salvando ? "…" : "⋮"}
                                                                </button>
                                                            </div>
                                                        </article>
                                                    </li>
                                                );
                                            })}
                                        </ul>
                                    )}
                                </section>
                            );
                        })}
                    </div>
                </main>
            </div>
        </>
    );
}