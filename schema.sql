/*room*/
create table
  public.room (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    calendar_id bigint null,
    room_name text not null,
    constraint Room_pkey primary key (id),
    constraint room_calendar_id_fkey foreign key (calendar_id) references calendar (id)
  ) tablespace pg_default;

/*users*/
create table
  public.users (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    name text not null,
    room_id bigint null,
    points integer null default 0,
    calendar_id bigint null,
    constraint Users_pkey primary key (id),
    constraint users_calendar_id_fkey foreign key (calendar_id) references calendar (id),
    constraint users_room_id_fkey foreign key (room_id) references room (id)
  ) tablespace pg_default;

  /*event*/
create table
  public.event (
    id bigint generated by default as identity,
    name text not null,
    start_time timestamp with time zone null,
    end_time timestamp with time zone null,
    calendar_id bigint null,
    description text null,
    constraint Event_pkey primary key (id),
    constraint event_calendar_id_fkey foreign key (calendar_id) references calendar (id)
  ) tablespace pg_default;

/*calendar*/
create table
  public.calendar (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    name text null,
    constraint Calendar_pkey primary key (id)
  ) tablespace pg_default;


/*chores*/
create table
  public.chores (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    chore_name text not null,
    assigned_user_id bigint null,
    completed boolean not null default false,
    points integer null,
    completed_at timestamp with time zone null,
    constraint chores_pkey primary key (id),
    constraint chores_assigned_user_id_fkey foreign key (assigned_user_id) references users (id)
  ) tablespace pg_default;

/*split*/
create table
  public.split (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    name text null,
    price real null,
    quantity integer null,
    user_added bigint null,
    constraint split_pkey primary key (id),
    constraint split_user_added_fkey foreign key (user_added) references users (id)
  ) tablespace pg_default;
