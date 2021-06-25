--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1
-- Dumped by pg_dump version 13.1

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: finance_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.finance_posts (
    post_id numeric,
    asset_id integer,
    matched_word character varying(300)
);


--
-- Name: holdings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.holdings (
    asset_id integer,
    ticker character varying(100),
    total_holding numeric,
    total_shares numeric
);


--
-- Name: identified_asset_post_with_price; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.identified_asset_post_with_price (
    tweet_id numeric NOT NULL,
    asset_id integer NOT NULL,
    matched_word character varying(300),
    asset_price_at_time numeric,
    post_date timestamp without time zone NOT NULL,
    is_last_market_close_price boolean NOT NULL
);


--
-- Name: manual_filter_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.manual_filter_rules (
    id integer NOT NULL,
    username character varying(100),
    asset_type character varying(30),
    asset_ticker character varying(15)
);


--
-- Name: manual_filter_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.manual_filter_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: manual_filter_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.manual_filter_rules_id_seq OWNED BY public.manual_filter_rules.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posts (
    post_id numeric NOT NULL,
    created_at timestamp without time zone,
    post_text text,
    symbols text[],
    username text,
    images text[],
    truncated boolean,
    is_retweet boolean,
    post_type character varying(20) DEFAULT 'Tweet'::character varying
);


--
-- Name: stock_nicknames; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stock_nicknames (
    asset_id numeric,
    nick_name character varying(50)
);


--
-- Name: tradeable_assets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tradeable_assets (
    asset_id integer NOT NULL,
    ticker character varying(10),
    asset_name character varying(300),
    asset_type character varying(50),
    current_rank integer,
    current_market_cap numeric,
    current_price integer,
    is_nick_name boolean
);


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    post_source_id numeric,
    asset_id integer,
    ticker character varying(100),
    transaction_type character varying(5),
    transaction_date timestamp without time zone,
    transaction_amount numeric,
    shares numeric
);


--
-- Name: manual_filter_rules id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manual_filter_rules ALTER COLUMN id SET DEFAULT nextval('public.manual_filter_rules_id_seq'::regclass);


--
-- Name: manual_filter_rules manual_filter_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manual_filter_rules
    ADD CONSTRAINT manual_filter_rules_pkey PRIMARY KEY (id);


--
-- Name: tradeable_assets public_companies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tradeable_assets
    ADD CONSTRAINT public_companies_pkey PRIMARY KEY (asset_id);


--
-- Name: posts tweets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT tweets_pkey PRIMARY KEY (post_id);


--
-- PostgreSQL database dump complete
--

