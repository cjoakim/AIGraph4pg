--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 17.2

-- Started on 2024-12-26 11:45:54 EST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 251 (class 1259 OID 123551)
-- Name: legal_cases; Type: TABLE; Schema: public; Owner: chjoakim
--

CREATE TABLE public.legal_cases (
    id bigint NOT NULL,
    name character varying(1024),
    name_abbreviation character varying(1024),
    case_url character varying(1024),
    decision_date date,
    court_name character varying(1024),
    citation_count integer,
    text_data text,
    json_data jsonb,
    embedding public.vector(1536)
);


ALTER TABLE public.legal_cases OWNER TO chjoakim;

--
-- TOC entry 250 (class 1259 OID 123550)
-- Name: legal_cases_id_seq; Type: SEQUENCE; Schema: public; Owner: chjoakim
--

CREATE SEQUENCE public.legal_cases_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.legal_cases_id_seq OWNER TO chjoakim;

--
-- TOC entry 5010 (class 0 OID 0)
-- Dependencies: 250
-- Name: legal_cases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: chjoakim
--

ALTER SEQUENCE public.legal_cases_id_seq OWNED BY public.legal_cases.id;


--
-- TOC entry 4853 (class 2604 OID 123554)
-- Name: legal_cases id; Type: DEFAULT; Schema: public; Owner: chjoakim
--

ALTER TABLE ONLY public.legal_cases ALTER COLUMN id SET DEFAULT nextval('public.legal_cases_id_seq'::regclass);


--
-- TOC entry 4861 (class 2606 OID 123558)
-- Name: legal_cases legal_cases_pkey; Type: CONSTRAINT; Schema: public; Owner: chjoakim
--

ALTER TABLE ONLY public.legal_cases
    ADD CONSTRAINT legal_cases_pkey PRIMARY KEY (id);


--
-- TOC entry 4854 (class 1259 OID 123562)
-- Name: idx_legal_cases_citation_count; Type: INDEX; Schema: public; Owner: chjoakim
--

CREATE INDEX idx_legal_cases_citation_count ON public.legal_cases USING btree (citation_count);


--
-- TOC entry 4855 (class 1259 OID 123561)
-- Name: idx_legal_cases_court_name; Type: INDEX; Schema: public; Owner: chjoakim
--

CREATE INDEX idx_legal_cases_court_name ON public.legal_cases USING btree (court_name);


--
-- TOC entry 4856 (class 1259 OID 123560)
-- Name: idx_legal_cases_decision_date; Type: INDEX; Schema: public; Owner: chjoakim
--

CREATE INDEX idx_legal_cases_decision_date ON public.legal_cases USING btree (decision_date);


--
-- TOC entry 4857 (class 1259 OID 123564)
-- Name: idx_legal_cases_ivfflat_embedding; Type: INDEX; Schema: public; Owner: chjoakim
--

CREATE INDEX idx_legal_cases_ivfflat_embedding ON public.legal_cases USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='50');


--
-- TOC entry 4858 (class 1259 OID 123563)
-- Name: idx_legal_cases_json_data_gin; Type: INDEX; Schema: public; Owner: chjoakim
--

CREATE INDEX idx_legal_cases_json_data_gin ON public.legal_cases USING gin (json_data);


--
-- TOC entry 4859 (class 1259 OID 123559)
-- Name: idx_legal_cases_name_abbreviation; Type: INDEX; Schema: public; Owner: chjoakim
--

CREATE INDEX idx_legal_cases_name_abbreviation ON public.legal_cases USING btree (name_abbreviation);


-- Completed on 2024-12-26 11:46:08 EST

--
-- PostgreSQL database dump complete
--

