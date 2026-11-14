import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import "./Movies.css";
import Header from "../components/Header.jsx";
import useLibrary from "../hooks/useLibrary";

export default function Movies() {

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

    async function alternarStatus(filme) {
        const id = filme.registroId;

        if (atualizando[id]) return;

        const novoStatus =
            filme.statusUsuario === "Quero Assistir"
                ? "Assistido"
                : "Quero Assistir";

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

            // Usa o status confirmado pelo backend.
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
        return <p>Carregando filmes...</p>;
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

    const filmes = (user.content ?? [])
        .filter((registro) => !idsExcluidos.includes(registro.id))
        .flatMap((registro) => {
            const conteudo = conteudosPorId.get(
                String(registro.mongo_id)
            );

            if (!conteudo || conteudo.type !== "movie") {
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

    const colunas = [
        {
            id: "watchlist-title",
            titulo: "Quero assistir",
            classeStatus: "status-pending",
            filmes: filmes.filter(
                (filme) => filme.statusUsuario === "Quero Assistir"
            ),
        },
        {
            id: "watched-title",
            titulo: "Assistidos",
            classeStatus: "status-watched",
            filmes: filmes.filter(
                (filme) => filme.statusUsuario === "Assistido"
            ),
        },
    ];

    return (
        <>
            <Header />

            <div className="movies-page">
                <main className="movies-content">
                    <section
                        className="movies-heading"
                        aria-labelledby="movies-title"
                    >
                        <div>
                            <h1 id="movies-title">🎬 Meus filmes</h1>
                            <p>
                                Organize o que quer assistir e acompanhe o que já viu.
                            </p>
                        </div>

                        <button className="add-movie-button" type="button">
                            + Adicionar filme
                        </button>
                    </section>

                    {erroStatus && (
                        <p role="alert">{erroStatus}</p>
                    )}

                    <div className="movies-columns">
                        {colunas.map((coluna) => (
                            <section
                                key={coluna.id}
                                className="movie-column"
                                aria-labelledby={coluna.id}
                            >
                                <header className="column-header">
                                    <h2 id={coluna.id}>
                    <span
                        className={`status-dot ${coluna.classeStatus}`}
                        aria-hidden="true"
                    />
                                        {coluna.titulo}
                                    </h2>

                                    <span className="movie-count">
                    {coluna.filmes.length}{" "}
                                        {coluna.filmes.length === 1
                                            }
                  </span>
                                </header>

                                {coluna.filmes.length === 0 ? (
                                    <p>Nenhum filme nesta lista.</p>
                                ) : (
                                    <ul className="movie-list">
                                        {coluna.filmes.map((filme) => {
                                            const salvando = Boolean(
                                                atualizando[filme.registroId]
                                            );

                                            const acao =
                                                filme.statusUsuario === "Quero Assistir"
                                                    ? "Marcar como assistido"
                                                    : "Mover para quero assistir";

                                            return (
                                                <li key={filme.registroId}>
                                                    <article className="movie-card">
                                                        <div className="movie-poster">
                                                            <img
                                                                src={filme.poster}
                                                                alt={`Capa de ${filme.title}`}
                                                            />
                                                        </div>

                                                        <div className="movie-info">
                                                            <h3>{filme.title}</h3>

                                                            <p className="movie-year">
                                                                {filme.date?.slice(0, 4)}
                                                            </p>

                                                            <ul
                                                                className="movie-genres"
                                                                aria-label="Gêneros"
                                                            >
                                                                {(filme.genres ?? []).map(
                                                                    (genero, index) => (
                                                                        <li key={`${genero}-${index}`}>
                                                                            {genero}
                                                                        </li>
                                                                    )
                                                                )}
                                                            </ul>
                                                        </div>

                                                        <div className="movie-actions">
                                                            <button
                                                                type="button"
                                                                onClick={() => excluirConteudo(filme.registroId)}
                                                                disabled={
                                                                    excluindo[filme.registroId] ||
                                                                    atualizando[filme.registroId]
                                                                }
                                                                aria-label={`Excluir ${filme.title} da biblioteca`}
                                                            >
                                                                x
                                                            </button>

                                                            <button
                                                                type="button"
                                                                onClick={() => alternarStatus(filme)}
                                                                disabled={salvando}
                                                                aria-label={acao}
                                                                title={acao}
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
                        ))}
                    </div>
                </main>
            </div>
        </>
    );
}