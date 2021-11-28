DROP DATABASE IF EXISTS `Oasis`;
CREATE DATABASE `Oasis`;
USE `Oasis`;
 
create table customer(
customer_id char(8) primary key NOT NULL,
customer_name char(20) NOT NULL,
customer_key char(18) NOT NULL,
customer_identity char(18) NOT NULL,
customer_phone char(18) NOT NULL
 );
 
 create table empoyee(
empoyee_id char(8) primary key NOT NULL,
empoyee_name char(20) NOT NULL,
empoyee_key char(18) NOT NULL
 );
 
 create table manager(
empoyee_id char(8) primary key NOT NULL,
empoyee_name char(20) NOT NULL,
empoyee_key char(18) NOT NULL
 );
 
 
create table occupancy( 
occupancy_id char(8) primary key NOT NULL,
occupancy_room char(7) NOT NULL,
occupancy_customer char(8) NOT NULL,
occupancy_day_in date NOT NULL,
occupancy_day_out date,
foreign key (occupancy_customer) references customer(customer_id)
 );
 
create table preorder( 
preorder_id char(8) primary key NOT NULL,
preorder_customer char(8) NOT NULL,
preorder_date date NOT NULL, 
preorder_type char(20) NOT NULL,
preorder_amount float ,
preorder_creditid char(18) NOT NULL,
check (preorder_type='prepay' or preorder_type='normol'),
foreign key (preorder_customer) references customer(customer_id)
 );
 