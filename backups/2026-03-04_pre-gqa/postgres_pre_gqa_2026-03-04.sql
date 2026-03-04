--
-- PostgreSQL database dump
--

\restrict WStC6gw8hZFtOUEzqfuP3TeMXx4ELijQUGH0VWgTEXhirVNchAsP87vS4wLcceF

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg12+1)
-- Dumped by pg_dump version 15.17 (Debian 15.17-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: predictive_matrix; Type: TABLE; Schema: public; Owner: atlas_admin
--

CREATE TABLE public.predictive_matrix (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    trigger_hash character varying(64) NOT NULL,
    a_priori_weight numeric(4,3) NOT NULL,
    ex_post_delta numeric(8,3) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT predictive_matrix_a_priori_weight_check CHECK (((a_priori_weight >= 0.0) AND (a_priori_weight <= 1.0)))
);


ALTER TABLE public.predictive_matrix OWNER TO atlas_admin;

--
-- Data for Name: predictive_matrix; Type: TABLE DATA; Schema: public; Owner: atlas_admin
--

COPY public.predictive_matrix (id, trigger_hash, a_priori_weight, ex_post_delta, created_at) FROM stdin;
\.


--
-- Name: predictive_matrix predictive_matrix_pkey; Type: CONSTRAINT; Schema: public; Owner: atlas_admin
--

ALTER TABLE ONLY public.predictive_matrix
    ADD CONSTRAINT predictive_matrix_pkey PRIMARY KEY (id);


--
-- Name: idx_predictive_matrix_trigger_hash; Type: INDEX; Schema: public; Owner: atlas_admin
--

CREATE INDEX idx_predictive_matrix_trigger_hash ON public.predictive_matrix USING btree (trigger_hash);


--
-- PostgreSQL database dump complete
--

\unrestrict WStC6gw8hZFtOUEzqfuP3TeMXx4ELijQUGH0VWgTEXhirVNchAsP87vS4wLcceF

